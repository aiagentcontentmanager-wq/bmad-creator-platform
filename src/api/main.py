"""FastAPI Application for BMAD System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(creators.router, prefix="/creators", tags=["Creators"])
app.include_router(content.router, prefix="/content", tags=["Content"])
app.include_router(publishing.router, prefix="/publish", tags=["Publishing"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])


@app.get("/")
async def root():
    return {"message": f"{settings.APP_NAME} API is running", "version": settings.APP_VERSION}


@app.get("/health")
async def health():
    return {"status": "ok"}
