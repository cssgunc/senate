"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

<<<<<<< gabriel
from app.routers import committees, health, leadership, news, senators
=======
from app.routers import (
    budget,
    carousel,
    districts,
    events,
    finance,
    health,
    news,
    pages,
    senators,
    staff,
)
>>>>>>> main

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
<<<<<<< gabriel
app.include_router(leadership.router)
app.include_router(committees.router)

=======
app.include_router(carousel.router)
app.include_router(districts.router)
app.include_router(staff.router)
app.include_router(finance.router)
app.include_router(budget.router)
app.include_router(pages.router)
app.include_router(events.router)
>>>>>>> main


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Senate API", "version": "0.1.0"}
