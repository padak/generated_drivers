"""
Base Driver Interface

Abstract base class defining the contract all drivers must implement.
This ensures consistent behavior across different APIs and services.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterator
from enum import Enum


class PaginationStyle(Enum):
    """How the driver handles pagination."""

    NONE = "none"  # No pagination support
    OFFSET = "offset"  # LIMIT/OFFSET style (SQL)
    CURSOR = "cursor"  # Cursor-based (Salesforce, GraphQL)
    PAGE_NUMBER = "page"  # Page-based (REST APIs)
    HYBRID = "hybrid"  # Both offset and cursor (mPOHODA)


@dataclass
class DriverCapabilities:
    """
    Describes what the driver can do.

    Agents read this to understand which operations are available
    and adjust their code generation accordingly.
    """

    read: bool = True
    write: bool = False
    update: bool = False
    delete: bool = False
    batch_operations: bool = False
    streaming: bool = False
    pagination: PaginationStyle = PaginationStyle.NONE
    query_language: Optional[str] = None  # e.g., "SOQL", "SQL", None
    max_page_size: Optional[int] = None
    supports_transactions: bool = False
    supports_relationships: bool = False


class BaseDriver(ABC):
    """
    Base class for all drivers.

    Every driver should inherit from this and implement required methods.
    This contract ensures agents can reliably use any driver implementation.
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

        IMPORTANT: Do not call this from subclass __init__().
        Instead, set attributes manually following the 4-phase pattern.

        Args:
            api_url: Base URL for API/database connection
            api_key: Authentication key/token (optional, can be loaded from env)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts for rate limiting
            debug: Enable debug logging (logs all API calls)
            **kwargs: Driver-specific options
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

        Example:
            # Reads MPOHODA_API_KEY and MPOHODA_API_URL from os.environ
            client = MPohodaDriver.from_env()

        Raises:
            AuthenticationError: If required env vars are missing
        """
        pass  # Implementation in subclass

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
        Discover all available objects/tables/entities.

        Returns:
            List of object names (e.g., ["Activities", "BusinessPartners", "Banks"])

        Example:
            objects = client.list_objects()
            # Returns: ["Activities", "BusinessPartners", "Banks", "BankAccounts", ...]
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
                }
            }

        Raises:
            ObjectNotFoundError: If object doesn't exist

        Example:
            fields = client.get_fields("BusinessPartner")
            # Returns: {
            #   "id": {"type": "string", "required": True, "label": "ID"},
            #   "name": {"type": "string", "required": False, "label": "Name"},
            #   ...
            # }
        """
        pass

    # Read Operations (REQUIRED)

    @abstractmethod
    def read(
        self,
        object_name: str,
        filters: Optional[Dict[str, Any]] = None,
        page_size: int = 50,
        page_number: int = 1,
    ) -> List[Dict[str, Any]]:
        """
        Read records from an object.

        Args:
            object_name: Name of object to read from
            filters: Optional filter conditions (varies by API)
            page_size: Maximum number of records to return
            page_number: Page number for pagination (1-indexed)

        Returns:
            List of dictionaries (one per record)

        Raises:
            ObjectNotFoundError: If object doesn't exist
            QuerySyntaxError: Invalid query/parameters
            RateLimitError: API rate limit exceeded (after retries)

        Example:
            results = client.read(
                "Activities",
                filters={"status": "active"},
                page_size=50
            )
            # Returns: [{"id": "...", "name": "...", ...}, ...]
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
            record = client.create("BusinessPartner", {
                "name": "Acme Corp",
                "taxNumber": "CZ123456789",
            })
            # Returns: {"id": "...", "name": "Acme Corp", ...}
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
        self, object_name: str, batch_size: int = 50
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Read records and yield results in batches (memory-efficient).

        Args:
            object_name: Name of object to read
            batch_size: Number of records per batch

        Yields:
            Batches of records as lists of dictionaries

        Example:
            for batch in client.read_batched("Activities", batch_size=50):
                process_batch(batch)  # Process 50 records at a time

        Note:
            Agent generates code with this pattern.
            Python runtime handles iteration (not the agent!).
        """
        raise NotImplementedError("Batched reading not supported by this driver")

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
            status = client.get_rate_limit_status()
            if status["remaining"] < 100:
                print("Warning: Only 100 API calls left!")
        """
        return {"remaining": None, "limit": None, "reset_at": None, "retry_after": None}

    def close(self):
        """
        Close connections and cleanup resources.

        Example:
            client = Driver.from_env()
            try:
                results = client.read("Activities")
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
