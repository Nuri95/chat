import json
from abc import ABC, abstractmethod


class BaseMessage(ABC):
    @property
    @abstractmethod
    def message_type(self):
        raise NotImplemented

    @abstractmethod
    def serialize(self):
        raise NotImplemented


class BadRequest(BaseMessage):
    message_type = 1

    def __init__(self, text: str):
        self.text = text

    def serialize(self) -> bytes:
        return self.text.encode("utf-8")

    @staticmethod
    def deserialize(payload: bytes):
        return BadRequest(payload.decode('utf-8'))


class MessageWelcome(BaseMessage):
    message_type = 2

    def __init__(self, name: str, secret: str):
        self.name = name
        self.secret = secret

    def serialize(self):
        return f"{self.name}__{self.secret}".encode('utf-8')

    @staticmethod
    def deserialize(payload):
        return MessageWelcome(*payload.decode('utf-8').split("__"))


class ClientMessage(BaseMessage):
    message_type = 3

    def __init__(self, text: str):
        self.text = text

    def serialize(self) -> bytes:
        return self.text.encode("utf-8")

    @staticmethod
    def deserialize(payload: bytes):
        return ClientMessage(payload.decode("utf-8"))


class ServerMessage(BaseMessage):
    message_type = 4

    def __init__(self, name: str, text: str):
        self.text = text
        self.name = name

    def serialize(self) -> bytes:
        return json.dumps([self.name,  self.text], ensure_ascii=False).encode("utf-8")

    @staticmethod
    def deserialize(payload: bytes):
        name, text = json.loads(payload.decode('utf-8'))
        return ServerMessage(name, text)


deserializers = {
    message_class.message_type: message_class.deserialize
    for message_class in [ServerMessage, ClientMessage, BadRequest, MessageWelcome]
}


