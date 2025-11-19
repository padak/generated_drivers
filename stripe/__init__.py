"""
Stripe Driver - Python API Driver for Stripe

A production-ready Python driver for the Stripe payment platform API.
Provides complete CRUD operations for Stripe resources with automatic
rate limiting, error handling, and cursor-based pagination.

Features:
- Bearer token authentication
- Cursor-based pagination (max 100 records per page)
- Automatic rate limit retry with exponential backoff
- Comprehensive error handling with structured exceptions
- Support for 30+ Stripe resource types
- Debug mode with detailed logging

Installation:
    pip install stripe-driver

Quick Start:
    from stripe_driver import StripeDriver

    # Create driver from environment variables
    client = StripeDriver.from_env()

    # Or with explicit credentials
    client = StripeDriver(api_key="sk_test_...")

    # Query resources
    products = client.read("products", limit=10)

    # Create resource
    product = client.create("products", {
        "name": "My Product",
        "type": "service"
    })

    # Update resource
    updated = client.update("products", "prod_123", {
        "name": "Updated Name"
    })

    # Delete resource
    client.delete("products", "prod_123")

    # Cleanup
    client.close()

Environment Variables:
    STRIPE_API_KEY: Stripe API key (required)
    STRIPE_BASE_URL: Stripe base URL (optional, default: https://api.stripe.com)

API Documentation:
    https://docs.stripe.com/api

License:
    See LICENSE file for details
"""

__version__ = "1.0.0"
__author__ = "Claude Code"
__license__ = "MIT"

from .client import StripeDriver
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
)

__all__ = [
    "StripeDriver",
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
]
