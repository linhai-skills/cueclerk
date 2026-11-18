"""Small JSON-RPC client for an existing Codex Unix WebSocket control socket.

Python standard library only. This client never starts a server, loads another
thread, changes permissions, or answers approval requests.
"""

import base64
from collections import deque
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import time


class RpcError(RuntimeError):
    """A definitive JSON-RPC error, distinct from an uncertain transport failure."""

    def __init__(self, code, message):
        self.code = code
        super().__init__(f"RPC {code}: {message}")


def default_socket():
    home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    return Path(os.environ.get("CUECLERK_CODEX_SOCKET", home / "app-server-control/app-server-control.sock"))


class CodexRPC:
    MAX_MESSAGE = 32 * 1024 * 1024

    def __init__(self, path=None, timeout=10):
        if os.name != "posix":
            raise RuntimeError("This adapter requires a Unix-like Codex host")
        self.path = Path(path or default_socket())
        info = self.path.stat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid():
            raise RuntimeError("Expected a Codex control socket owned by the current user")
        self.timeout = timeout
        self.buffer = bytearray()
        self.events = deque()
        self.sequence = 0
        self.fragments = bytearray()
        self.fragmented = False
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(timeout)
            self.sock.connect(str(self.path))
            key = base64.b64encode(os.urandom(16)).decode("ascii")
            request = (
                "GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n\r\n"
            )
            self.sock.sendall(request.encode("ascii"))
            while b"\r\n\r\n" not in self.buffer:
                self._receive()
                if len(self.buffer) > 16384:
                    raise RuntimeError("Oversized WebSocket handshake")
            header, rest = bytes(self.buffer).split(b"\r\n\r\n", 1)
            self.buffer = bytearray(rest)
            lines = header.decode("ascii").split("\r\n")
            fields = dict(line.lower().split(":", 1) for line in lines[1:] if ":" in line)
            expected = base64.b64encode(hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
            ).digest()).decode("ascii")
            # Header values are case sensitive for Sec-WebSocket-Accept.
            actual = dict(line.split(":", 1) for line in lines[1:] if ":" in line)
            accept = next((v.strip() for k, v in actual.items() if k.lower() == "sec-websocket-accept"), "")
            if (lines[0].split()[1] != "101" or accept != expected
                    or fields.get("upgrade", "").strip() != "websocket"):
                raise RuntimeError("Codex control socket rejected the WebSocket handshake")
            self.call("initialize", {"clientInfo": {
                "name": "cueclerk", "title": "CueClerk", "version": "1.0.0"
            }})
            self.send({"method": "initialized"})
        except BaseException:
            self.close()
            raise

    def close(self):
        self.sock.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _receive(self):
        data = self.sock.recv(65536)
        if not data:
            raise ConnectionError("Codex control socket closed")
        self.buffer.extend(data)

    def _frame(self, opcode, data):
        size = len(data)
        if size > self.MAX_MESSAGE:
            raise RuntimeError("WebSocket message exceeds size limit")
        if size < 126:
            header = bytes([0x80 | opcode, 0x80 | size])
        elif size < 65536:
            header = bytes([0x80 | opcode, 0xFE]) + struct.pack("!H", size)
        else:
            header = bytes([0x80 | opcode, 0xFF]) + struct.pack("!Q", size)
        mask = os.urandom(4)
        self.sock.sendall(header + mask + bytes(v ^ mask[i % 4] for i, v in enumerate(data)))

    def send(self, message):
        self._frame(1, json.dumps(message, ensure_ascii=False).encode("utf-8"))

    def _message(self, timeout):
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Timed out waiting for Codex")
            self.sock.settimeout(remaining)
            if len(self.buffer) < 2:
                self._receive()
                continue
            first, second = self.buffer[:2]
            if first & 0x70 or second & 0x80:
                raise RuntimeError("Unsupported WebSocket frame")
            size, offset = second & 127, 2
            extra = 2 if size == 126 else 8 if size == 127 else 0
            if len(self.buffer) < offset + extra:
                self._receive()
                continue
            if extra:
                size = int.from_bytes(self.buffer[offset:offset + extra], "big")
                offset += extra
            if size > self.MAX_MESSAGE:
                raise RuntimeError("Oversized WebSocket frame")
            if len(self.buffer) < offset + size:
                self._receive()
                continue
            data = bytes(self.buffer[offset:offset + size])
            del self.buffer[:offset + size]
            opcode, final = first & 15, bool(first & 128)
            if opcode >= 8 and (not final or size > 125):
                raise RuntimeError("Invalid WebSocket control frame")
            if opcode == 8:
                raise ConnectionError("Codex closed the WebSocket")
            if opcode == 9:
                self._frame(10, data)
                continue
            if opcode == 10:
                continue
            if opcode == 1 and not self.fragmented:
                self.fragments = bytearray(data)
                self.fragmented = not final
            elif opcode == 0 and self.fragmented:
                self.fragments.extend(data)
                self.fragmented = not final
            else:
                raise RuntimeError("Unexpected WebSocket message type")
            if len(self.fragments) > self.MAX_MESSAGE:
                raise RuntimeError("Oversized fragmented message")
            if final:
                message = json.loads(self.fragments.decode("utf-8"))
                self.fragments.clear()
                if not isinstance(message, dict):
                    raise RuntimeError("Expected a JSON-RPC object")
                return message

    def call(self, method, params):
        self.sequence += 1
        request_id = self.sequence
        self.sock.settimeout(self.timeout)
        self.send({"id": request_id, "method": method, "params": params})
        deadline = time.monotonic() + self.timeout
        while True:
            message = self._message(max(0, deadline - time.monotonic()))
            if message.get("id") == request_id and "method" not in message:
                if "error" in message:
                    error = message["error"]
                    raise RpcError(error.get("code"), error.get("message", "request failed"))
                return message["result"]
            if "method" in message:
                self.events.append(message)

    def event(self, timeout=1):
        if self.events:
            return self.events.popleft()
        return self._message(timeout)

    def snapshot(self, thread_id, full=False):
        thread = self.call("thread/read", {"threadId": thread_id})["thread"]
        turns = self.call("thread/turns/list", {
            "threadId": thread_id, "limit": 1, "sortDirection": "desc",
            "itemsView": "full" if full else "summary"
        })["data"]
        if thread.get("id") != thread_id or not turns:
            raise RuntimeError("Cannot identify the current thread and turn")
        return thread, turns[0]
