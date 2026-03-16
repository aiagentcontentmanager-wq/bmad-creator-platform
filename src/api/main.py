"""FastAPI Application for BMAD System."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.core.config import settings
from src.api.routes import auth, creators, content, publishing, analytics, finance

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (landing page)
static_dir = Path(__file__).parent.parent.parent / "landing"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(creators.router, prefix="/creators", tags=["Creators"])
app.include_router(content.router, prefix="/content", tags=["Content"])
app.include_router(publishing.router, prefix="/publish", tags=["Publishing"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])

LANDING_HTML = static_dir / "index.html"


@app.get("/", response_class=HTMLResponse)
async def root():
    if LANDING_HTML.exists():
        return LANDING_HTML.read_text(encoding="utf-8")
    return f"<h1>{settings.APP_NAME}</h1><p>API is running</p>"


@app.get("/health")
async def health():
    return {"status": "ok"}
