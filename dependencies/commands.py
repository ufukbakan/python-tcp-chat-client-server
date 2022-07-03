class Command:
    def __init__(self, action: str, body: object) -> None:
        self.action = action
        self.body = body