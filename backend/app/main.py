"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import feed, feedback, onboarding, papers, saved, settings, university


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: could create tables here for dev, but prefer Alembic
    yield
    # Shutdown


app = FastAPI(
    title="Research Radar API",
    description="Personalized research paper discovery and tracking",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(onboarding.router)
app.include_router(feed.router)
app.include_router(feedback.router)
app.include_router(university.router)
app.include_router(papers.router)
app.include_router(saved.router)
app.include_router(settings.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "research-radar"}
