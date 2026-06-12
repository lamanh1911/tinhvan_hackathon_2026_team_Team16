from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


# Common error constructors
def not_found(resource: str) -> AppError:
    return AppError(404, "NOT_FOUND", f"{resource} not found")


def validation_error(message: str) -> AppError:
    return AppError(400, "VALIDATION_ERROR", message)


def invalid_status(message: str) -> AppError:
    return AppError(400, "INVALID_STATUS", message)


def integration_error(service: str) -> AppError:
    return AppError(503, "INTEGRATION_ERROR", f"{service} is unavailable")


def invalid_card_type(message: str = "Uploaded image is not a valid business card") -> AppError:
    return AppError(422, "INVALID_CARD_TYPE", message)


def wrong_card_type(message: str = "Uploaded image appears to be a bank card or membership card, not a business card") -> AppError:
    return AppError(422, "WRONG_CARD_TYPE", message)
