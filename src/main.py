from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.api.v1 import v1_router
from src.config import get_settings
from src.database import Base, SessionLocal, engine
from src.models import CallLog, Patient  # noqa: F401
from src.utils.logging import configure_logging, get_logger
from src.utils.response import envelope
from src.utils.seed import seed_if_empty

settings = get_settings()
configure_logging(settings.LOG_LEVEL)
logger = get_logger()

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_if_empty(db)

app = FastAPI(title=settings.APP_TITLE, version=settings.APP_VERSION)

# Core REST API routes (spec-compliant paths).
app.include_router(v1_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code, content=envelope(error=str(exc.detail))
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    errors = exc.errors()
    message = errors[0]["msg"] if errors else "Validation error"
    return JSONResponse(status_code=422, content=envelope(error=message))


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content=envelope(error=str(exc)))


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500, content=envelope(error="Internal server error")
    )


@app.get("/health")
def health():
    return {"status": "ok"}
