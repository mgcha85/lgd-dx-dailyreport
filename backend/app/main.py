from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import upload, classification, history, settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="일보 자동 분류 시스템",
    description="LLM을 활용한 일보 자동 분류 API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(classification.router, prefix="/api", tags=["Classification"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(settings.router, prefix="/api", tags=["Settings"])


@app.get("/")
async def root():
    return {"message": "일보 자동 분류 시스템 API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
