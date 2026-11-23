class AppError(Exception):
    """Base class for domain errors that map to an HTTP status."""

    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ValidationFailed(AppError):
    status_code = 422


class PayloadTooLarge(AppError):
    status_code = 413


class UpstreamError(AppError):
    status_code = 502


class IngestionError(Exception):
    """Raised when a document cannot be processed."""
