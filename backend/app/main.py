"""FastAPI application entry point"""

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    budget,
    carousel,
    committees,
    districts,
    events,
    finance,
    health,
    leadership,
    legislation,
    news,
    pages,
    senators,
    staff,
)
from app.routers.admin import committees as admin_committees
<<<<<<< HEAD
from app.routers.admin import legislation as admin_legislation
=======
from app.routers.admin import leadership as admin_leadership
>>>>>>> b10e0533512e1de0849cd82f2f9b9104932e5f8b
from app.routers.admin import news as admin_news
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
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(news.router)
app.include_router(senators.router)
app.include_router(leadership.router)
app.include_router(committees.router)
app.include_router(carousel.router)
app.include_router(districts.router)
app.include_router(staff.router)
app.include_router(finance.router)
app.include_router(budget.router)
app.include_router(pages.router)
app.include_router(events.router)
app.include_router(legislation.router)
app.include_router(admin_news.router)

# Include Admin routers
app.include_router(admin_committees.router)
app.include_router(admin_legislation.router)
app.include_router(admin_senators.router)
app.include_router(admin_leadership.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Senate API", "version": "0.1.0"}
