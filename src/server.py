from threading import Thread
from typing import Union

from networking.message import Message, MessageWelcome, IMessage
from networking.message_socket import MessageSocket
from networking.server_socket import ServerSocket


class AcceptConnectionThread(Thread):
    def __init__(self, server: ServerSocket):
        self.server_socket = server
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            self.server_socket.listen_connections(self.on_connect)
        except Exception as e:
            print(str(e))

    def on_connect(self, connection: MessageSocket):
        print('Получена новая коннекция' + connection.get_name())
        # if self.connection.get_name() not in connections:
            # self.connection.send('What is your name?')
        handle_connection = HandleConnectionThread(connection)
        handle_connection.start()
        # TODO сохранить порожденные потоки чтобы потом над всеми сделать join


class HandleConnectionThread(Thread):
    def __init__(self, connection: MessageSocket):
        self.connection = connection
        super().__init__()
        self.daemon = True
        self.handlers = {
            MessageWelcome.message_type: self.on_welcome,
            Message.message_type: self.on_message,
        }

    def run(self):
        try:
            self.connection.listen_messages(self.handle)
        except Exception as e:
            print(str(e))

    def handle(self, msg: IMessage):
        self.handlers[msg.message_type](msg)

    def on_welcome(self, msg: MessageWelcome):
        self.connection.data['name'] = msg.name
        print(f'{self.connection.get_name()} -> {msg.name}')

    def on_message(self, msg: Message):
        name = self.connection.data.get('name') or self.connection.get_name()
        return_message = Message(msg.text)
        self.connection.send(return_message)
        print(f'{name}: {return_message.text}')


server_socket = ServerSocket()
s = AcceptConnectionThread(server_socket)
s.start()
s.join()
