import threading
import traceback
from threading import Thread

from config.config import get_connection
from networking.message import (
    ServerMessage,
    MessageWelcome,
    BaseMessage,
    ClientMessage,
    BadRequest,
)
from networking.message_socket import MessageSocket
from networking.server_socket import ServerSocket


class Connections:
    def __init__(self):
        self.connections = []

    def get_connections(self):
        return self.connections

    def add_connection(self, connection: MessageSocket):
        if connection not in self.connections:
            self.connections.append(connection)

    def send(self, message: ServerMessage):
        for connection in self.connections:
            connection.send(message)

    def remove_connection(self, connection) -> None:
        self.connections = [con for con in self.connections if con != connection]


class AcceptConnection:
    def __init__(self, server: ServerSocket, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        self.server_socket = server
        super().__init__()
        self.connections = Connections()
        self.child_threads = []

    def run(self):
        print('start accept connection thread')
        try:
            self.server_socket.listen_connections(self.on_connect, self.check_alive_connections)
        except Exception as e:
            print(str(e))
        except KeyboardInterrupt:
            self.is_stopped.set()

        self.server_socket.close()
        print('finished accept connection thread')

        # дожидаюсь завершения работы потомков
        for child_thread in self.child_threads:
            child_thread.join()

    def check_alive_connections(self):
        alive = []
        not_alive = []
        for child_thread in self.child_threads:
            if child_thread.is_alive():
                alive.append(child_thread)
            else:
                not_alive.append(child_thread)

        self.child_threads = alive
        for child_thread in not_alive:
            print('удален мертвый thread')
            child_thread.join()  # мусор прибрать. сделать вид что дожидаемся завершения работы

    def on_connect(self, connection: MessageSocket):
        print(f'Получена новая коннекция: {connection.get_name()}')

        self.connections.add_connection(connection)

        handle_connection = HandleConnectionThread(connection, self.connections, self.is_stopped)
        handle_connection.start()
        handle_connection.is_alive()
        # TODO сохранить порожденные потоки чтобы потом над всеми сделать join
        self.child_threads.append(handle_connection)


class HandleConnectionThread(Thread):
    def __init__(self, connection: MessageSocket, connections: Connections, is_stopped: threading.Event):
        self.is_stopped = is_stopped
        self.connection = connection
        super().__init__()
        self.handlers = {
            MessageWelcome.message_type: self.on_welcome,
            ClientMessage.message_type: self.on_message
        }
        self.connections = connections

    def run(self):
        print('start handle connection')
        try:
            self.connection.listen_messages(self.handle)
        except Exception as e:
            print(str(e))
            print(traceback.format_exc())
        print('была     ', len(self.connections.connections))
        self.connections.remove_connection(self.connection)
        print('стала ', len(self.connections.connections))
        print('finished handle connection')

    def handle(self, msg: BaseMessage):
        self.handlers[msg.message_type](msg)

    def on_welcome(self, msg: MessageWelcome):
        self.connection.data['name'] = msg.name
        self.connection.data['secret'] = msg.secret

        with get_connection() as cursor:
            cursor.execute(
                "SELECT * from client where username=%(username)s and secret=%(secret)s",
                {"secret": msg.secret, "username": msg.name},
            )
            client = cursor.fetchall()
            if not client:
                cursor.execute(
                    'INSERT INTO client (secret, username) values (%(secret)s, %(username)s)',
                    {"secret": msg.secret, "username": msg.name},
                )

        print(f'{self.connection.get_name()} -> {msg.name}')

    def on_message(self, msg: ClientMessage):
        name = self.connection.data.get('name')
        if not name:
            return self.connection.send(BadRequest('Введите имя и секретное слово'))
        return_message = ServerMessage(name, msg.text)
        self.connections.send(return_message)

        print(f'{name}: {return_message.text}')


is_stopped = threading.Event()
server_socket = ServerSocket(is_stopped)
s = AcceptConnection(server_socket, is_stopped)
print('server thread')

s.run()