"""
Base Driver Interface (Driver Design v2.0)

Defines the abstract interface that all drivers must implement.
Agents use this interface to generate code for any driver.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterator
from enum import Enum


class PaginationStyle(Enum):
    """How the driver handles pagination"""
    NONE = "none"              # No pagination support
    OFFSET = "offset"          # LIMIT/OFFSET style (SQL, REST APIs)
    CURSOR = "cursor"          # Cursor-based (Salesforce, GraphQL)
    PAGE_NUMBER = "page"       # Page-based (REST APIs)


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
            api_url: Base URL for API/database connection
            api_key: API key for authentication (optional)
            access_token: OAuth access token (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Number of retry attempts for rate limiting (default: 3)
            debug: Enable debug logging (logs all API calls)
            **kwargs: Driver-specific options

        Raises:
            AuthenticationError: Invalid credentials
            ConnectionError: Cannot reach API
        """
        self.api_url = api_url
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

        # Validate credentials at init time (fail fast!)
        self._validate_connection()

    @classmethod
    def from_env(cls, **kwargs) -> "BaseDriver":
        """
        Create driver instance from environment variables.

        Example:
            # Reads APIFY_API_KEY and APIFY_API_URL from os.environ
            client = ApifyDriver.from_env()

        Returns:
            Initialized driver instance

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

        Example:
            capabilities = client.get_capabilities()
            if capabilities.write:
                # Agent can generate create() calls
        """
        pass

    # Discovery Methods (REQUIRED)

    @abstractmethod
    def list_objects(self) -> List[str]:
        """
        Discover all available objects/resources/endpoints.

        Returns:
            List of object/resource names

        Example:
            objects = client.list_objects()
            # Returns: ["actors", "datasets", "key-value-stores", "runs", ...]
        """
        pass

    @abstractmethod
    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete field schema for an object/resource.

        Args:
            object_name: Name of object (case-sensitive!)

        Returns:
            Dictionary with field definitions:
            {
                "field_name": {
                    "type": "string|integer|float|boolean|datetime|...",
                    "description": "Field description",
                    "required": bool,
                }
            }

        Raises:
            ObjectNotFoundError: If object doesn't exist
        """
        pass

    # Read Operations (REQUIRED)

    @abstractmethod
    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results.

        Args:
            query: Query/endpoint path in driver's format
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of dictionaries (one per record)

        Raises:
            QuerySyntaxError: Invalid query syntax
            RateLimitError: API rate limit exceeded (after retries)
            ConnectionError: Cannot reach API

        Example:
            results = client.read(
                "/datasets/xyz/items",
                limit=100
            )
        """
        pass

    # Write Operations (OPTIONAL)

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record/resource.

        Args:
            object_name: Name of object to create
            data: Field values as dictionary

        Returns:
            Created record with ID

        Raises:
            NotImplementedError: If driver doesn't support write operations
            ValidationError: If data is invalid
        """
        raise NotImplementedError("Write operations not supported by this driver")

    def update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing record.

        Args:
            object_name: Name of object
            record_id: ID of record to update
            data: Field values to update

        Returns:
            Updated record

        Raises:
            NotImplementedError: If driver doesn't support updates
            ObjectNotFoundError: If record doesn't exist
        """
        raise NotImplementedError("Update operations not supported by this driver")

    def delete(self, object_name: str, record_id: str) -> bool:
        """
        Delete a record.

        Args:
            object_name: Name of object
            record_id: ID of record to delete

        Returns:
            True if successful

        Raises:
            NotImplementedError: If driver doesn't support delete

        Note:
            Agents should RARELY generate delete operations!
            Always require explicit user approval for deletes.
        """
        raise NotImplementedError("Delete operations not supported by this driver")

    # Pagination / Streaming (OPTIONAL)

    def read_batched(
        self,
        query: str,
        batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute query and yield results in batches (memory-efficient).

        Args:
            query: Query in driver's native format
            batch_size: Number of records per batch

        Yields:
            Batches of records as lists of dictionaries

        Example:
            for batch in client.read_batched("/datasets/xyz/items", batch_size=1000):
                process_batch(batch)
        """
        raise NotImplementedError("Batched reading not supported by this driver")

    # Utility Methods

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status (if supported by API).

        Returns:
            {
                "remaining": int or None,    # Requests remaining
                "limit": int or None,        # Total limit
                "reset_at": str or None,     # ISO timestamp when limit resets
                "retry_after": int or None   # Seconds to wait (if rate limited)
            }

        Example:
            status = client.get_rate_limit_status()
            if status["remaining"] and status["remaining"] < 10:
                print("Warning: Only 10 API calls left!")
        """
        return {"remaining": None, "limit": None, "reset_at": None, "retry_after": None}

    def close(self):
        """
        Close connections and cleanup resources.

        Example:
            client = ApifyDriver.from_env()
            try:
                results = client.read("/datasets/xyz/items")
            finally:
                client.close()
        """
        pass

    # Internal Methods

    def _validate_connection(self):
        """
        Validate connection at __init__ time (fail fast!).

        Raises:
            AuthenticationError: Invalid credentials
            ConnectionError: Cannot reach API
        """
        pass
