"""
Authentication Routes - DISABLED
All authentication has been removed from the application.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])

# All authentication endpoints have been disabled
# The application is now fully public with no login required
