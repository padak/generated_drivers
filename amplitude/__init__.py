"""
Amplitude Analytics Driver

A production-ready Python driver for Amplitude's Analytics APIs.

Features:
- Batch Event Upload: Ingest events in bulk (up to 2000 per batch)
- Identify API: Update user properties without sending events
- Export API: Export historical event data
- Automatic retry on rate limits with exponential backoff
- Comprehensive error handling with structured exceptions
- Full type hints for IDE autocomplete

Quick Start:
    >>> from amplitude import AmplitudeDriver
    >>> driver = AmplitudeDriver.from_env()
    >>> # Upload events
    >>> events = [
    ...     {"user_id": "u1", "event_type": "signup"},
    ...     {"user_id": "u2", "event_type": "login"},
    ... ]
    >>> result = driver.create_batch(events)
    >>> print(f"Ingested {result['events_ingested']} events")
    >>> driver.close()

Authentication:
    Set environment variable:
        export AMPLITUDE_API_KEY="your_api_key"

Documentation:
    - README.md: Comprehensive usage guide
    - examples/: Working code examples
    - API reference: See docstrings in client.py
"""

__version__ = "1.0.0"
__author__ = "Amplitude Driver Team"

from .client import (
    AmplitudeDriver,
    DriverCapabilities,
    PaginationStyle,
)
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
    # Main driver
    "AmplitudeDriver",
    # Capabilities
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
