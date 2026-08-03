class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)


class ConflictError(Exception):
    def __init__(self, message="Resource already exists"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)
