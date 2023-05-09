import socket
import threading

from networking.message_socket import MessageSocket


class ServerSocket:
    def __init__(self, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        ip, port = socket.gethostname(), 5002
        self.header_length = 9
        self.message_byte = self.header_length + 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.2)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(5)
        self.stopped = False

    def listen_connections(self, on_connect, check_alive_connections):
        while True:
            try:
                client_socket, client_address = self.sock.accept()
                message_socket = MessageSocket(client_socket, self.is_stopped)
                on_connect(message_socket)
            except socket.timeout:
                check_alive_connections()
                if self.is_stopped.is_set():
                    return

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()