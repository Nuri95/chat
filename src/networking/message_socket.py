import struct
import socket
import threading

from networking.message import deserializers, BaseMessage


class MessageSocket:
    def __init__(self, sock: socket, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        self.sock = sock
        self.sock.settimeout(0.2)
        self.header_length = 9
        self.data = {}

    def listen_messages(self, on_message):
        while True:
            try:
                header = self.sock.recv(self.header_length)
            except socket.timeout:
                if self.is_stopped.is_set():
                    self.sock.close()
                    return
                continue

            if not len(header):
                self.sock.close()
                break

            len_message, type_message = struct.unpack('LB', header)
            payload = self.sock.recv(len_message)
            try:
                message = deserializers[type_message](payload)
            except KeyError:
                self.sock.close()
                break
            else:
                on_message(message)

    def send(self, message: BaseMessage):
        bytes = message.serialize()
        self.sock.send(struct.pack('LB', len(bytes), message.message_type) + bytes)

    def get_name(self) -> str:
        ip, port = self.sock.getpeername()
        return ip + ':' + str(port)
