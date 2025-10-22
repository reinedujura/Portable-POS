"""Custom Exception Classes for Backend"""

class DatabaseException(Exception):
    """Base exception for database operations"""
    pass

class ValidationException(DatabaseException):
    """Raised when data validation fails"""
    pass

class NotFoundError(DatabaseException):
    """Raised when a requested resource is not found"""
    pass

class DuplicateError(DatabaseException):
    """Raised when attempting to create a duplicate entry"""
    pass
