from fastapi import APIRouter

from src.api.v1.routes import calls, patients, tools

v1_router = APIRouter()

v1_router.include_router(patients.router)
v1_router.include_router(calls.router)
v1_router.include_router(tools.router)
