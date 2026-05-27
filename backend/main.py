import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import CORS_ORIGINS
from routers import auth, exams, analytics, anti_cheat, recommendations

app = FastAPI(
    title="Adaptive AI Assessment Platform",
    description="AI-Powered Computerized Adaptive Testing (CAT) with IRT Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(exams.router)
app.include_router(analytics.router)
app.include_router(anti_cheat.router)
app.include_router(recommendations.router)

@app.get("/")
async def root():
    return {
        "name": "Adaptive AI Assessment Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "auth": "/auth",
            "exam": "/exam",
            "analytics": "/analytics",
            "anti_cheat": "/anti-cheat"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
