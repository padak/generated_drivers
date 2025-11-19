"""
Apify Driver - Production-ready Python API driver for Apify API

Quick Start:
    >>> from apify_driver import ApifyDriver
    >>>
    >>> # Load credentials from environment
    >>> client = ApifyDriver.from_env()
    >>>
    >>> # List all actors
    >>> actors = client.read("/actors", limit=50)
    >>> print(f"Found {len(actors)} actors")
    >>>
    >>> # Cleanup
    >>> client.close()

Environment Variables:
    APIFY_API_TOKEN: Your Apify API token (required)
    APIFY_API_URL: API base URL (optional, default: https://api.apify.com/v2)

Token Location: https://console.apify.com/settings/integrations

Features:
    - Full CRUD operations on Actors, Datasets, Runs, Tasks, etc.
    - Automatic retry with exponential backoff on rate limits
    - Offset-based pagination for large datasets
    - Memory-efficient batch operations
    - Comprehensive error handling with structured exceptions
    - Debug logging for troubleshooting

Capabilities:
    - Read: ✓ (list, get, query operations)
    - Write: ✓ (create, update, delete operations)
    - Batch Operations: ✓ (read_batched for memory efficiency)
    - Streaming: ✓ (large dataset support)
    - Pagination: ✓ (offset-based LIMIT/OFFSET)

Error Handling:
    >>> from apify_driver import (
    ...     ApifyDriver,
    ...     AuthenticationError,
    ...     RateLimitError,
    ...     ObjectNotFoundError,
    ... )
    >>>
    >>> try:
    ...     client = ApifyDriver.from_env()
    ...     data = client.read("/invalid-endpoint")
    ... except ObjectNotFoundError as e:
    ...     print(f"Not found: {e.message}")
    ... except RateLimitError as e:
    ...     print(f"Rate limited. Retry after {e.details['retry_after']}s")
    ... except AuthenticationError as e:
    ...     print(f"Auth failed: {e.message}")

Example Scripts:
    See examples/ directory for complete working examples.

Production Deployment:
    1. Set APIFY_API_TOKEN environment variable
    2. Use ApifyDriver.from_env() to initialize
    3. Wrap API calls in try/except
    4. Use client.close() in finally block
    5. Enable debug=True for troubleshooting

Rate Limits:
    - Global: 250,000 requests/minute per user
    - Per-resource default: 60 requests/second
    - Driver automatically retries on HTTP 429

Documentation:
    - API Reference: https://docs.apify.com/api/v2
    - Python Client: https://docs.apify.com/api/client/python
"""

from .client import ApifyDriver
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

__version__ = "1.0.0"
__author__ = "Agent-Generated"
__all__ = [
    # Driver
    "ApifyDriver",
    # Base classes
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
    "NotImplementedError",
]
