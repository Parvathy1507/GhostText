from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth import router as auth_router
from app.database import init_db
from app.routes.analysis import router as analysis_router


BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="GhostText",
    description="AI Document Forensics & Hidden Instruction Detector",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    return response


app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)

app.include_router(analysis_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": "GhostText",
    }