class APIException(Exception):
    pass


class AlreadyExistsException(APIException):
    pass


class DoesNotExistException(APIException):
    pass


class InvalidTableException(APIException):
    pass


class AuthException(APIException):
    pass


class InvalidCredentialsException(AuthException):
    pass


class PermissionDeniedException(AuthException):
    pass
