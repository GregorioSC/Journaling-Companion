# dao/exceptions.py


class DAOError(Exception):
    """Base class for all DAO-related errors."""

    pass


class UniqueConstraintError(DAOError):
    """Raised when a unique constraint (e.g., email already exists) is violated."""

    pass


class NotFoundError(DAOError):
    """Raised when a requested record is not found in the database."""

    pass


class ConnectionError(DAOError):
    """Raised when a database connection cannot be established."""

    pass
