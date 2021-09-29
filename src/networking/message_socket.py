import struct
import sys
from socket import socket

from networking.message import Message


class MessageSocket:
    def __init__(self, sock: socket):
        self.sock = sock
        self.header_length = 9

    def listen_messages(self, on_message):
        while True:
            header = self.sock.recv(self.header_length)
            if not len(header):
                sys.exit()

            len_message, type_message = struct.unpack('LB', header)
            payload = self.sock.recv(len_message)

            message = Message.deserialize(payload)
            # TODO декодировать не только message, в on_message принимать не только message
            on_message(message)

    def send(self, message: Message):
        bytes = message.serialize()
        print('отправляем байты на сервер')
        self.sock.send(struct.pack('LB', len(bytes), message.message_type) + bytes)

    def get_name(self) -> str:
        ip, port = self.sock.getpeername()
        return ip + ':' + str(port)
