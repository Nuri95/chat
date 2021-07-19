import socket
import struct
import sys
import threading


class EventHook(object):

    def __init__(self):
        self.__handlers = []

    def __iadd__(self, handler):
        self.__handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.__handlers.remove(handler)
        return self

    def emit(self, *args, **keywargs):
        for handler in self.__handlers:
            handler(*args, **keywargs)


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
    sock = None

    def __init__(self):
        self.port = 5002
        self.header_length = 9
        self.ip = socket.gethostname()
        self.onMessage = EventHook()

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.ip, self.port))
        self.sock = client_socket

    def start(self):
        print('Start Client')
        self.listen_messages()

    def listen_messages(self):
        while True:
            header = self.sock.recv(self.header_length)
            if not len(header):
                sys.exit()

            len_message, type_message = struct.unpack('LB', header)
            payload = self.sock.recv(len_message)
            answer_server = Message.deserialize(payload)
            print('Сервер ответил', answer_server)

            self.onMessage.emit(answer_server)

    def send(self, package):
        bytes = package.serialize()
        print('отправляем байты на сервер')
        self.sock.send(struct.pack('LB', len(bytes), package.TYPE)+bytes)


class User:
    def __init__(self, s: Socket):
        s.onMessage += self.onMessage
        self.s = s

    def onMessage(self, message: Message):
        print('New msg: ' + message.text)

    def start(self):
        print('Введите сообщение:')
        msg = input()
        s.send(Message(msg))
        pass


s = Socket()
socket_thread = threading.Thread(target=s.start)
user_thread = threading.Thread(target=User(s).start)
socket_thread.start()
user_thread.start()
user_thread.join()
socket_thread.join()

