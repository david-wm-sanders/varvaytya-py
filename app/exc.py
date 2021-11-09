class VarvaytyaException(Exception):
    issue = ""


class VarvaytyaValidationError(VarvaytyaException):
    issue = "validation failed"


class DigestNotSupportedError(VarvaytyaValidationError):
    issue = "rid auth only"


class GetMissingArgError(VarvaytyaValidationError):
    issue = "missing argument(s)"


class HashNotIntError(VarvaytyaValidationError):
    issue = "hash not int"


class UsernameTooLongError(VarvaytyaValidationError):
    issue = "username too long"


class UsernameFormatError(VarvaytyaValidationError):
    issue = "bad username format"


class RidLengthError(VarvaytyaValidationError):
    issue = "bad rid length"


class RidNotHexError(VarvaytyaValidationError):
    issue = "rid not hex"


class RealmDigestLengthError(VarvaytyaValidationError):
    issue = "bad realm digest length"


class RealmDigestNotHexError(VarvaytyaValidationError):
    issue = "realm digest not hex"


class RealmNotFoundError(VarvaytyaException):
    issue = "imaginary realm"


class RealmDigestIncorrectError(VarvaytyaException):
    issue = "realm digest incorrect"


class PlayerNotFound(VarvaytyaException):
    issue = "player not found"


class AccountNotFoundError(VarvaytyaException):
    issue = "account not found"


class RidIncorrectError(VarvaytyaException):
    issue = "rid incorrect"
