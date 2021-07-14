import socket


class Socket:
    def __init__(self):
        ip, port = socket.gethostname(), 5000
        self.header_length = 10
        self.message_byte = self.header_length + 1024

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip, port))
        self.sock.listen()
        self.clients = []

    def start(self):
        print('Start Server')
        self.listen_message()

    def listen_message(self):
        while True:
            # data, addres = self.sock.recvfrom(1024)
            data, addres = self.sock.accept()
            # self.sock.sendto(data, addres)
            print(addres)
            if addres not in self.clients:
                self.clients.append(addres)

            # for client in self.clients:
            #     if client == addres:
            #         continue  # Не отправлять клиенту который прислал
                self.sock.sendto(data, addres)

s = Socket()
s.start()
