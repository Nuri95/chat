import socket

from networking.message_socket import MessageSocket


class ServerSocket:
    def __init__(self):
        ip, port = socket.gethostname(), 5002
        self.header_length = 9
        self.message_byte = self.header_length + 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen(5)

    def listen_connections(self, on_connect):
        while True:
            client_socket, client_address = self.sock.accept()
            message_socket = MessageSocket(client_socket)
            on_connect(message_socket)