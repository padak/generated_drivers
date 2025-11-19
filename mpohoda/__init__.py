"""
mPOHODA Python Driver

Production-ready driver for mPOHODA accounting software API.

Installation:
    pip install mpohoda-driver

Quick Start:
    from mpohoda import MPohodaDriver

    # Initialize from environment
    driver = MPohodaDriver.from_env()

    # Read data
    activities = driver.read("Activities")

    # Create record
    partner = driver.create("BusinessPartners", {
        "name": "Acme Corp",
        "taxNumber": "CZ123456789"
    })

Authentication:
    Set environment variables:
    - MPOHODA_API_KEY: API key for authentication
    - MPOHODA_CLIENT_ID + MPOHODA_CLIENT_SECRET: OAuth2 credentials
    - MPOHODA_ACCESS_TOKEN: Pre-obtained OAuth2 token (optional)
    - MPOHODA_BASE_URL: Custom API URL (optional)

See: https://api.mpohoda.cz/doc for API documentation
"""

__version__ = "1.0.0"
__author__ = "Claude Code"
__all__ = [
    "MPohodaDriver",
    "BaseDriver",
    "DriverCapabilities",
    "PaginationStyle",
    "DriverError",
    "AuthenticationError",
    "ConnectionError",
    "ObjectNotFoundError",
    "FieldNotFoundError",
    "QuerySyntaxError",
    "RateLimitError",
    "ValidationError",
    "TimeoutError",
    "NotImplementedError",
]

from .client import MPohodaDriver
from .base import BaseDriver, DriverCapabilities, PaginationStyle
from .exceptions import (
    DriverError,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    FieldNotFoundError,
    QuerySyntaxError,
    RateLimitError,
    ValidationError,
    TimeoutError,
    NotImplementedError,
)
