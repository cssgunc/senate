"""FastAPI application entry point"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import health, leadership, news, senators
from app.routers.admin import leadership as admin_leadership
from app.routers.admin import senators as admin_senators

load_dotenv()

app = FastAPI(
    title="Senate API",
    description="Backend API for Senate application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(news.router)
app.include_router(senators.router)

# leadership router (public)
app.include_router(leadership.router)

# Include Admin routers that exist
app.include_router(admin_senators.router)
app.include_router(admin_leadership.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Senate API", "version": "0.1.0"}
