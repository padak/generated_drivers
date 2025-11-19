"""
PostHog Python Driver

A production-ready Python driver for the PostHog API.

Features:
- Full CRUD operations on PostHog resources
- Automatic pagination and retry on rate limits
- Structured error handling
- Debug mode for troubleshooting

Installation:
    pip install posthog-driver

Quick Start:
    from posthog_driver import PostHogDriver

    # Initialize from environment
    driver = PostHogDriver.from_env()

    # List available resources
    objects = driver.list_objects()

    # Read data
    dashboards = driver.read("/dashboards")

    # Create resource
    new_dashboard = driver.create("dashboards", {
        "name": "My Dashboard"
    })

    # Cleanup
    driver.close()

Environment Variables:
    POSTHOG_API_KEY: Personal API key (required)
    POSTHOG_API_URL: API base URL (optional, default: https://app.posthog.com/api)
    POSTHOG_PROJECT_ID: Project ID (optional)

Rate Limits:
    - CRUD operations: 480 req/min, 4800 req/hour
    - Query endpoint: 2400 req/hour
    - Public POST endpoints: Unlimited

For more information, visit: https://posthog.com/docs/api
"""

__version__ = "1.0.0"
__author__ = "PostHog"
__license__ = "MIT"

from .client import PostHogDriver
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
    # Driver
    "PostHogDriver",
    # Base classes and data structures
    "BaseDriver",
    "DriverCapabilities",
    "PaginationStyle",
    # Exceptions
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
