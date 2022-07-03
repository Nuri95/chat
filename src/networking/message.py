from abc import ABC, abstractmethod

print(2)
print(3)
class BaseMessage(ABC):
    @property
    @abstractmethod
    def message_type(self):
        raise NotImplemented

    @abstractmethod
    def serialize(self):
        raise NotImplemented


class Message(BaseMessage):
    message_type = 1

    def __init__(self, text: str):
        self.text = text

    def serialize(self):
        return self.text.encode('utf-8')

    @staticmethod
    def deserialize(payload):
        return Message(payload.decode('utf-8'))


class MessageWelcome(BaseMessage):
    message_type = 2

    def __init__(self, name: str):
        self.name = name

    def serialize(self):
        return self.name.encode('utf-8')

    @staticmethod
    def deserialize(payload):
        return MessageWelcome(payload.decode('utf-8'))


deserializers = {
    message_class.message_type: message_class.deserialize
    for message_class in [Message, MessageWelcome]
}


