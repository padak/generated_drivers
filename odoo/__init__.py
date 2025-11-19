"""
Odoo Driver - Production-grade Python driver for Odoo External RPC API

A comprehensive driver for Odoo 19.0+ with full CRUD support, domain-based
filtering, batch operations, and comprehensive error handling.

Example:
    from odoo_driver import OdooDriver

    # Load from environment
    client = OdooDriver.from_env()

    # Query data
    partners = client.read("[['active', '=', True]]", limit=100)

    # Create record
    record = client.create("res.partner", {"name": "New Company"})

    # Cleanup
    client.close()
"""

__version__ = "1.0.0"
__author__ = "Generated with Claude Code"
__license__ = "MIT"

from .client import OdooDriver
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
from .base import BaseDriver, DriverCapabilities, PaginationStyle

__all__ = [
    "OdooDriver",
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
