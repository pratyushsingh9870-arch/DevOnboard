from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .config import get_settings
from .api import repos, docs

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Developer Onboarding Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Allow ALL origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(repos.router)
app.include_router(docs.router)

@app.get("/")
async def root():
    return {"message": "Welcome to DevOnboard API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}