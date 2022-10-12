class ErrorObject():
    def __init__(self, errorCode=400, errorMessage="Something went wrong"):
        self.errorCode = errorCode
        self.errorMessage = errorMessage
        return
