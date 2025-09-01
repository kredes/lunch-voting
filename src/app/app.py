"""
Entry point for the application.
"""

from fastapi import FastAPI

from app.routers import restaurants, users, voting


app = FastAPI()

app.include_router(restaurants.router)
app.include_router(users.router)
app.include_router(voting.router)
