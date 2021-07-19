import socket
import struct


class Message:
    TYPE = 1

    def __init__(self, text: str):
        self.text = text

    def serialize(self):
        return self.text.encode('utf-8')

    @staticmethod
    def deserialize(payload):
        return Message(payload.decode('utf-8'))


class Socket:
    def __init__(self):
        ip, port = socket.gethostname(), 5002
        self.header_length = 9
        self.message_byte = self.header_length + 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.clients = []

    def start(self):
        print('Start Server')
        self.listen_message()

    def receive_message(self, client_socket):
        message_header = client_socket.recv(self.header_length)

        if not len(message_header):
            return False

        len_message, type_message = struct.unpack('LB', message_header)
        payload = client_socket.recv(len_message)
        return Message.deserialize(payload)

    def send(self, package, client_socket):
        bytes = package.serialize()
        client_socket.send(struct.pack('LB', len(bytes), package.TYPE)+bytes)

    def listen_message(self):
        while True:
            client_socket, client_addres = self.sock.accept()
            data = self.receive_message(client_socket)

            if not data:
                continue

            if client_addres not in self.clients:
                self.clients.append(client_addres)

            self.send(data, client_socket)


s = Socket()
s.start()
