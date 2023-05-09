import os
import signal
import readline
import threading
from typing import Callable

from networking.message import ServerMessage, MessageWelcome, ClientMessage, BaseMessage, BadRequest
from networking.remote_socket import RemoteSocket


class ReceivingThread(threading.Thread):
    def __init__(self, socket: RemoteSocket, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        self.socket = socket
        super().__init__()
        self.daemon = True
        self.handlers: dict[int, Callable] = {
            ServerMessage.message_type: self.on_server_message,
            BadRequest.message_type: self.on_bad_request
        }

    def run(self):
        print("receiving run")
        try:
            self.socket.listen_messages(self.on_message)
        except Exception as e:
            print(str(e))
        print("receiving run finished")
        os.kill(os.getpid(), signal.SIGINT)

    def on_message(self, msg: BaseMessage):
        self.handlers[msg.message_type](msg)

    def on_bad_request(self, msg: BadRequest):
        print(f"Сервер прислал: {msg.text}")

    def on_server_message(self, msg: ServerMessage):
        print(f"Получено сообщение {msg.name}: {msg.text}")


class Sending:
    def __init__(self, socket: RemoteSocket, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        self.socket = socket
        super().__init__()

    def run(self):
        while True:
            msg = input()
            print(f'смс {msg}')

            if msg.startswith('Я '):
                _, name, _, secret = msg.split(' ')
                self.socket.send(MessageWelcome(name, secret))
            else:
                self.socket.send(ClientMessage(msg))
            print('Отправлено сообщение ' + msg)


is_stopped = threading.Event()
remote_socket = RemoteSocket(is_stopped)
receiver = ReceivingThread(remote_socket, is_stopped)
sender = Sending(remote_socket, is_stopped)
receiver.start()

# главный поток спит и ждем прерывания. затем выставляет флаг
# для дочерних потоков и дожидается их завершения
try:
    sender.run()
except KeyboardInterrupt:
    is_stopped.set()

receiver.join()

