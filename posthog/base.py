"""
Base Driver Interface

Defines the abstract base class and data structures that all drivers must implement.
This is the contract between agents and drivers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Iterator
from enum import Enum


class PaginationStyle(Enum):
    """How the driver handles pagination"""

    NONE = "none"  # No pagination support
    OFFSET = "offset"  # LIMIT/OFFSET style (SQL)
    CURSOR = "cursor"  # Cursor-based (Salesforce, GraphQL)
    PAGE_NUMBER = "page"  # Page-based (REST APIs)


@dataclass
class DriverCapabilities:
    """
    What the driver can do.

    Used by agents to discover what operations are supported.

    Attributes:
        read: Can execute read/query operations
        write: Can create new records
        update: Can update existing records
        delete: Can delete records
        batch_operations: Supports batch/bulk operations
        streaming: Supports streaming/Server-Sent Events responses
        pagination: Pagination style used by API
        query_language: Query language (HogQL, SQL, SOQL, etc.) or None
        max_page_size: Maximum records per page (None if unlimited)
        supports_transactions: Supports transactional operations
        supports_relationships: Supports relationship/join operations

    Example:
        >>> capabilities = driver.get_capabilities()
        >>> if capabilities.write:
        ...     # Agent can generate create() calls
        ...     driver.create("dashboards", {"name": "My Dashboard"})
    """

    read: bool = True
    write: bool = False
    update: bool = False
    delete: bool = False
    batch_operations: bool = False
    streaming: bool = False
    pagination: PaginationStyle = PaginationStyle.NONE
    query_language: Optional[str] = None
    max_page_size: Optional[int] = None
    supports_transactions: bool = False
    supports_relationships: bool = False


class BaseDriver(ABC):
    """
    Abstract base class for all drivers.

    Every driver should inherit from this and implement required methods.

    The driver is a bridge between the Agent (generates Python code) and
    External Systems (APIs, databases, etc.).

    Key principle: Driver documents HOW to write Python code. Agent generates it.

    Attributes:
        api_url: Base URL for API/database connection
        api_key: API key/token for authentication (optional)
        timeout: Request timeout in seconds
        max_retries: Number of retry attempts for failed requests
        debug: Enable debug logging

    Example:
        >>> driver = PostHogDriver.from_env()
        >>> capabilities = driver.get_capabilities()
        >>> objects = driver.list_objects()
        >>> dashboards = driver.read("SELECT * FROM dashboards")
        >>> driver.close()
    """

    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize the driver.

        Args:
            api_url: Base URL for API/database connection
            api_key: Authentication key/token (optional, can be loaded from env)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Number of retry attempts for rate limiting (default: 3)
            debug: Enable debug logging (default: False)
            **kwargs: Driver-specific options

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If cannot reach API

        Note:
            Subclasses should NOT call super().__init__().
            Instead, set parent attributes manually:

            def __init__(self, api_url, api_key, **kwargs):
                # Phase 1: Custom attributes
                self.custom_field = kwargs.get('custom_field')

                # Phase 2: Parent attributes (manual assignment)
                self.api_url = api_url
                self.api_key = api_key
                self.timeout = timeout or 30
                self.max_retries = max_retries or 3
                self.debug = debug

                # Phase 3: Create session
                self.session = self._create_session()

                # Phase 4: Validate connection
                self._validate_connection()
        """
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

        # Validate credentials at init time (fail fast!)
        self._validate_connection()

    @classmethod
    def from_env(cls, **kwargs) -> "BaseDriver":
        """
        Create driver instance from environment variables.

        This classmethod loads credentials from environment variables.
        Subclasses should override this to specify which env vars to use.

        Args:
            **kwargs: Additional arguments passed to __init__

        Returns:
            Configured driver instance

        Raises:
            AuthenticationError: If required environment variables are missing

        Example:
            >>> # Reads POSTHOG_API_KEY from os.environ
            >>> driver = PostHogDriver.from_env()
        """
        raise NotImplementedError("Subclass must implement from_env()")

    @abstractmethod
    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities so agent knows what it can do.

        Returns:
            DriverCapabilities with boolean flags for features

        Example:
            >>> capabilities = driver.get_capabilities()
            >>> if capabilities.write:
            ...     # Agent can generate create() calls
        """
        pass

    # Discovery Methods (REQUIRED)

    @abstractmethod
    def list_objects(self) -> List[str]:
        """
        Discover all available objects/tables/entities.

        Returns:
            List of object names

        Example:
            >>> objects = driver.list_objects()
            >>> print(objects)
            ['dashboards', 'datasets', 'batch_exports', 'persons', 'events']
        """
        pass

    @abstractmethod
    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete field schema for an object.

        Args:
            object_name: Name of object (case-sensitive!)

        Returns:
            Dictionary with field definitions:
            {
                "field_name": {
                    "type": "string|integer|float|boolean|datetime|...",
                    "label": "Human-readable name",
                    "required": bool,
                    "nullable": bool,
                    "max_length": int (for strings),
                    "references": str (for foreign keys)
                }
            }

        Raises:
            ObjectNotFoundError: If object doesn't exist

        Example:
            >>> fields = driver.get_fields("dashboards")
            >>> print(fields.keys())
            dict_keys(['id', 'name', 'description', 'created_at', ...])
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
            query: Query in driver's native language (HogQL, SQL, etc.)
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of dictionaries (one per record)

        Raises:
            QuerySyntaxError: Invalid query syntax
            RateLimitError: API rate limit exceeded (after retries)

        Example:
            >>> results = driver.read(
            ...     "SELECT id, name FROM dashboards WHERE created_at > '2025-01-01'",
            ...     limit=100
            ... )
            >>> for dashboard in results:
            ...     print(dashboard['name'])
        """
        pass

    # Write Operations (OPTIONAL - depends on capabilities)

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record.

        Args:
            object_name: Name of object to create
            data: Field values as dictionary

        Returns:
            Created record with ID

        Raises:
            NotImplementedError: If driver doesn't support write operations
            ValidationError: If data is invalid

        Example:
            >>> dashboard = driver.create("dashboards", {
            ...     "name": "My Dashboard",
            ...     "description": "Test dashboard"
            ... })
            >>> print(dashboard['id'])
        """
        raise NotImplementedError("Write operations not supported by this driver")

    def update(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
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
            ValidationError: If data is invalid

        Example:
            >>> updated = driver.update("dashboards", "123", {
            ...     "name": "Updated Name"
            ... })
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

        Example:
            >>> success = driver.delete("dashboards", "123")
            >>> print(f"Deleted: {success}")
        """
        raise NotImplementedError("Delete operations not supported by this driver")

    # Pagination / Streaming (OPTIONAL)

    def read_batched(
        self, query: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute query and yield results in batches (memory-efficient).

        Args:
            query: Query in driver's native language
            batch_size: Number of records per batch

        Yields:
            Batches of records as lists of dictionaries

        Example:
            >>> for batch in driver.read_batched(
            ...     "SELECT * FROM events", batch_size=1000
            ... ):
            ...     process_batch(batch)

        Note:
            Agent generates code with this pattern.
            Python runtime handles iteration (not the agent!).
        """
        raise NotImplementedError("Batched reading not supported by this driver")

    # Low-Level API (OPTIONAL - for REST APIs)

    def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Call a REST API endpoint directly (low-level access).

        Args:
            endpoint: API endpoint path (e.g., "/dashboards")
            method: HTTP method ("GET", "POST", "PUT", "DELETE")
            params: URL query parameters
            data: Request body (for POST/PUT)
            **kwargs: Additional request options

        Returns:
            Response data as dictionary

        Example:
            >>> result = driver.call_endpoint(
            ...     endpoint="/dashboards",
            ...     method="GET",
            ...     params={"limit": 50}
            ... )
        """
        raise NotImplementedError("Low-level endpoint calls not supported by this driver")

    # Utility Methods

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status (if supported by API).

        Returns:
            {
                "remaining": int,     # Requests remaining
                "limit": int,         # Total limit
                "reset_at": str,      # ISO timestamp when limit resets
                "retry_after": int    # Seconds to wait (if rate limited)
            }

        Example:
            >>> status = driver.get_rate_limit_status()
            >>> if status["remaining"] < 10:
            ...     print("Warning: Only 10 API calls left!")
        """
        return {"remaining": None, "limit": None, "reset_at": None, "retry_after": None}

    def close(self):
        """
        Close connections and cleanup resources.

        Example:
            >>> driver = PostHogDriver.from_env()
            >>> try:
            ...     results = driver.read("SELECT * FROM dashboards")
            ... finally:
            ...     driver.close()
        """
        pass

    # Internal Methods

    def _validate_connection(self):
        """
        Validate connection at __init__ time (fail fast!).

        This method is called during initialization to ensure credentials
        are valid before any operations are attempted.

        Raises:
            AuthenticationError: Invalid credentials
            ConnectionError: Cannot reach API
        """
        pass
