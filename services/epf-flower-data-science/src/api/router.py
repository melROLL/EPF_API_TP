"""API Router for Fast API."""
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from src.api.routes import hello
from .routes import data  # Add this import

router.include_router(data.router, prefix="/data", tags=["data"])  # Add this line


router = APIRouter()

@router.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    return "/docs"
