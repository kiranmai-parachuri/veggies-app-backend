from veggies_service.conf.error_object import ErrorObject


class NotFoundException(Exception):
    """Raise when something goes wrong in the request validation"""

    def __init__(self, entity="Object", errorObject=None):
        if errorObject:
            self.errorObject = errorObject
        else:
            self.errorObject = ErrorObject(errorCode=404,
                                           errorMessage=(entity + " not Found"))

    def __str__(self):
        return str(self.errorObject.errorMessage)


class BadRequest(Exception):
    """Raise when something goes wrong in the request validation"""

    def __init__(self, errorMessage="Bad Request", errorCode=400):
        self.errorObject = ErrorObject(errorMessage=errorMessage,
                                       errorCode=errorCode)

    def __str__(self):
        return str(self.errorObject.errorMessage)


class UnauthorisedException(Exception):
    def __init__(self, message="Authorization Failure"):
        self.errorObject = ErrorObject(errorMessage=message, errorCode=401)

    def _serialize(self):
        return self.errorObject.errorMessage


class GenericCustomException(Exception):
    def __init__(self, message='Something went Wrong', code=400):
        error_object = ErrorObject()
        error_object.errorCode = code
        error_object.errorMessage = message
        self.errorObject = error_object


class AlreadyExist(Exception):
    """Raise when something goes wrong in the request validation"""

    def __init__(self, entity="Object", errorObject=None):
        if errorObject:
            self.errorObject = errorObject
        else:
            self.errorObject = ErrorObject(errorCode=404, errorMessage=(
                entity + " Already Exists"))

    def __str__(self):
        return str(self.errorObject.errorMessage)


class InternalServerError(Exception):
    """Raise when something goes wrong"""

    def __init__(self, errorObject=None):
        if errorObject:
            self.errorObject = errorObject
        else:
            self.errorObject = ErrorObject(errorCode=500,
                                           errorMessage='Internal server error')

    def __str__(self):
        return str(self.errorObject.errorMessage)


class ValidationException(Exception):
    """Raise when something goes wrong in the request validation"""

    def __init__(self, errorMessage="Validation failure", errorCode=400):
        self.errorObject = ErrorObject(errorMessage=errorMessage,
                                       errorCode=errorCode)

    def __str__(self):
        return str(self.errorObject.errorMessage)
