from threading import Thread

from networking.message import Message, MessageWelcome, BaseMessage
from networking.message_socket import MessageSocket
from networking.server_socket import ServerSocket


class Connections:
    def __init__(self):
        self.connections = []

    def get_connections(self):
        return self.connections

    def add_connection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)

    def send(self, message: Message):
        for connection in self.connections:
            connection.send(message)

class AcceptConnectionThread(Thread):
    def __init__(self, server: ServerSocket):
        self.server_socket = server
        super().__init__()
        self.daemon = True
        self.connections = Connections()

    def run(self):
        try:
            self.server_socket.listen_connections(self.on_connect)
        except Exception as e:
            print(str(e))

    def on_connect(self, connection: MessageSocket):
        print('Получена новая коннекция' + connection.get_name())

        self.connections.add_connection(connection)

        handle_connection = HandleConnectionThread(connection, self.connections)
        handle_connection.start()
        # TODO сохранить порожденные потоки чтобы потом над всеми сделать join


class HandleConnectionThread(Thread):
    def __init__(self, connection: MessageSocket, connections: Connections):
        self.connection = connection
        super().__init__()
        self.daemon = True
        self.handlers = {
            MessageWelcome.message_type: self.on_welcome,
            Message.message_type: self.on_message,
        }
        self.connections = connections

    def run(self):
        try:
            self.connection.listen_messages(self.handle)
        except Exception as e:
            print(str(e))

    def handle(self, msg: BaseMessage):
        self.handlers[msg.message_type](msg)

    def on_welcome(self, msg: MessageWelcome):
        self.connection.data['name'] = msg.name
        print(f'{self.connection.get_name()} -> {msg.name}')

    def on_message(self, msg: Message):
        name = self.connection.data.get('name') or self.connection.get_name()
        return_message = Message(msg.text)
        self.connections.send(return_message)

        print(f'{name}: {return_message.text}')


server_socket = ServerSocket()
s = AcceptConnectionThread(server_socket)
s.start()
s.join()
