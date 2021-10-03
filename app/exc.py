class EnlistdException(Exception):
    issue = ""


class EnlistdValidationError(EnlistdException):
    issue = "validation failed"


class DigestNotSupportedError(EnlistdValidationError):
    issue = "rid auth only"


class GetMissingArgError(EnlistdValidationError):
    issue = "missing argument(s)"


class HashNotIntError(EnlistdValidationError):
    issue = "hash not int"


class UsernameTooLongError(EnlistdValidationError):
    issue = "username too long"


class UsernameFormatError(EnlistdValidationError):
    issue = "bad username format"


class RidLengthError(EnlistdValidationError):
    issue = "bad rid length"


class RidNotHexError(EnlistdValidationError):
    issue = "rid not hex"


class RealmDigestLengthError(EnlistdValidationError):
    issue = "bad realm digest length"


class RealmDigestNotHexError(EnlistdValidationError):
    issue = "realm digest not hex"


class RealmNotFoundError(EnlistdException):
    issue = "imaginary realm"


class RealmDigestIncorrectError(EnlistdException):
    issue = "realm digest incorrect"


class PlayerNotFoundError(EnlistdException):
    issue = "player not found"


class RidIncorrectError(EnlistdException):
    issue = "rid incorrect"
