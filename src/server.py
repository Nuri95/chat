from threading import Thread

from networking.message import Message
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
        handle_connection = HandleConnectionThread(connection)
        handle_connection.start()
        # TODO сохранить порожденные потоки чтобы потом над всеми сделать join


class HandleConnectionThread(Thread):
    def __init__(self, connection: MessageSocket):
        self.connection = connection
        super().__init__()
        self.daemon = True

    def run(self):
        try:
            self.connection.listen_messages(self.on_message)
        except Exception as e:
            print(str(e))

    def on_message(self, msg: Message):
        return_message = Message(msg.text)
        print(f'Из соединения {self.connection.get_name()} получено сообщение {return_message.text}')
        self.connection.send(return_message)


server_socket = ServerSocket()
s = AcceptConnectionThread(server_socket)
s.start()
s.join()
