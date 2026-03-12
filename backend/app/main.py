"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    budget,
    carousel,
    districts,
    events,
    finance,
    health,
    legislation,
    news,
    pages,
    senators,
    staff,
)

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
app.include_router(carousel.router)
app.include_router(districts.router)
app.include_router(staff.router)
app.include_router(finance.router)
app.include_router(budget.router)
app.include_router(pages.router)
app.include_router(events.router)
app.include_router(legislation.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Senate API", "version": "0.1.0"}
