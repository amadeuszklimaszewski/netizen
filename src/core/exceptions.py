class APIException(Exception):
    pass


class AlreadyExistsException(APIException):
    pass


class DoesNotExistException(APIException):
    pass


class InvalidTableException(APIException):
    pass


class FriendRequestAlreadyHandled(APIException):
    pass


class GroupRequestAlreadyHandled(APIException):
    pass


class AlreadyActivatedAccountException(APIException):
    pass


class AuthException(APIException):
    pass


class InvalidCredentialsException(AuthException):
    pass


class PermissionDeniedException(AuthException):
    pass


class InvalidConfirmationTokenException(AuthException):
    pass
