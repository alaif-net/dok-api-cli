class DokError(Exception):
    pass


class ConfigError(DokError):
    pass


class AuthError(DokError):
    pass


class NotFoundError(DokError):
    pass


class ApiError(DokError):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(message)
