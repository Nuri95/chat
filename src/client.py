from signal import signal
from threading import Thread

from networking.message import Message, MessageWelcome
from networking.remote_socket import RemoteSocket


class ReceivingThread(Thread):
    def __init__(self, socket: RemoteSocket):
        self.socket = socket
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            self.socket.listen_messages(self.on_message)
        except Exception as e:
            print(str(e))

    def on_message(self, msg: Message):
        print('Получено сообщение ' + msg.text)


class SendingThread(Thread):
    def __init__(self, socket: RemoteSocket):
        self.socket = socket
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            while True:
                msg = input()
                if msg.startswith('Я '):
                    self.socket.send(MessageWelcome(msg[2:]))
                else:
                    self.socket.send(Message(msg))
                print('Отправлено сообщение ' + msg)
        except Exception as e:
            print(str(e))


remote_socket = RemoteSocket()
receiver = ReceivingThread(remote_socket)
sender = SendingThread(remote_socket)

receiver.start()
sender.start()

receiver.join()

sender.join()

