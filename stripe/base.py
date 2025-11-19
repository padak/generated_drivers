"""
Stripe Driver - Base Classes

Defines the BaseDriver interface and common data structures.
All drivers inherit from BaseDriver and implement required methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterator
from enum import Enum


class PaginationStyle(Enum):
    """How the driver handles pagination"""

    NONE = "none"  # No pagination support
    OFFSET = "offset"  # LIMIT/OFFSET style (SQL)
    CURSOR = "cursor"  # Cursor-based (Stripe, GraphQL)
    PAGE_NUMBER = "page"  # Page-based (REST APIs)


@dataclass
class DriverCapabilities:
    """What the driver can do"""

    read: bool = True
    write: bool = False
    update: bool = False
    delete: bool = False
    batch_operations: bool = False
    streaming: bool = False
    pagination: PaginationStyle = PaginationStyle.NONE
    query_language: Optional[str] = None  # "SOQL", "SQL", "MongoDB Query", None
    max_page_size: Optional[int] = None
    supports_transactions: bool = False
    supports_relationships: bool = False


class BaseDriver(ABC):
    """
    Base class for all drivers.
    Every driver should inherit from this and implement required methods.
    """

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize the driver.

        Args:
            api_url: Base URL for API connection
            api_key: API key for authentication (optional)
            access_token: Bearer token for authentication (optional)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for rate limiting
            debug: Enable debug logging (logs all API calls)
            **kwargs: Driver-specific options
        """
        self.api_url = api_url
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

    @classmethod
    def from_env(cls, **kwargs) -> "BaseDriver":
        """
        Create driver instance from environment variables.

        Returns:
            Driver instance

        Raises:
            AuthenticationError: If required env vars are missing
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities so agent knows what it can do.

        Returns:
            DriverCapabilities with boolean flags for features
        """
        pass

    # Discovery Methods (REQUIRED)

    @abstractmethod
    def list_objects(self) -> List[str]:
        """
        Discover all available objects/resources.

        Returns:
            List of object names
        """
        pass

    @abstractmethod
    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete field schema for an object.

        Args:
            object_name: Name of object (case-sensitive!)

        Returns:
            Dictionary with field definitions
        """
        pass

    # Read Operations (REQUIRED)

    @abstractmethod
    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results.

        Args:
            query: Query in driver's native language
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of dictionaries (one per record)
        """
        pass

    # Write Operations (OPTIONAL)

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record."""
        raise NotImplementedError("Write operations not supported by this driver")

    def update(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record."""
        raise NotImplementedError("Update operations not supported by this driver")

    def delete(self, object_name: str, record_id: str) -> bool:
        """Delete a record."""
        raise NotImplementedError("Delete operations not supported by this driver")

    # Pagination (OPTIONAL)

    def read_batched(
        self, query: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """Execute query and yield results in batches."""
        raise NotImplementedError("Batched reading not supported by this driver")

    # Low-Level API (OPTIONAL)

    def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Call a REST API endpoint directly."""
        raise NotImplementedError("Low-level endpoint calls not supported by this driver")

    # Utility Methods

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        return {"remaining": None, "limit": None, "reset_at": None, "retry_after": None}

    def close(self):
        """Close connections and cleanup resources."""
        pass

    # Internal Methods

    def _validate_connection(self):
        """Validate connection at __init__ time."""
        pass
