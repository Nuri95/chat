class Message:

    def __init__(self, text: str):
        self.text = text
        self.message_type = 1

    def serialize(self):
        return self.text.encode('utf-8')

    @staticmethod
    def deserialize(payload):
        return Message(payload.decode('utf-8'))
