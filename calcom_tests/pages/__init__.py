"""
pages/__init__.py — Paquete de Page Objects para la suite E2E de Cal.com.
"""

from .login_page import LoginPage
from .booking_page import BookingPage

__all__ = ["LoginPage", "BookingPage"]
