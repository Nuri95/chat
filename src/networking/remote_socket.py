import socket

from networking.message_socket import MessageSocket


class RemoteSocket(MessageSocket):
    def __init__(self):
        self.port = 5002
        self.ip = socket.gethostname()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        super().__init__(client_socket)
