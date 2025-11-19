"""
Apify API Driver (v2.0)

Production-ready driver for Apify API with bug prevention measures.

Features:
- Bearer token authentication with automatic retry
- Offset-based pagination support
- Comprehensive error handling with structured exceptions
- Debug logging for troubleshooting
- Memory-efficient batch operations

Example:
    >>> client = ApifyDriver.from_env()
    >>> actors = client.read("/actors")
    >>> client.close()
"""

import logging
import os
import time
from typing import List, Dict, Any, Optional, Iterator

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Bug Prevention #5: Support both package and standalone imports
try:
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
        TimeoutError as DriverTimeoutError,
    )
except ImportError:
    # Fallback for standalone execution (tests, scripts)
    from base import BaseDriver, DriverCapabilities, PaginationStyle
    from exceptions import (
        DriverError,
        AuthenticationError,
        ConnectionError,
        ObjectNotFoundError,
        FieldNotFoundError,
        QuerySyntaxError,
        RateLimitError,
        ValidationError,
        TimeoutError as DriverTimeoutError,
    )


class ApifyDriver(BaseDriver):
    """
    Apify API driver with full CRUD operations on Actors, Datasets, Key-Value Stores, and more.

    Authentication:
    - Primary: Bearer token in Authorization header
    - Token location: https://console.apify.com/settings/integrations

    Features:
    - Automatic retry with exponential backoff on rate limits (HTTP 429)
    - Offset-based pagination for large datasets
    - Batch operations for datasets
    - Debug logging of all API calls

    Example:
        >>> # Option 1: Load from environment
        >>> client = ApifyDriver.from_env()
        >>>
        >>> # Option 2: Explicit credentials
        >>> client = ApifyDriver(
        ...     api_url="https://api.apify.com/v2",
        ...     api_key="your_api_token"
        ... )
        >>>
        >>> # List all actors
        >>> actors = client.read("/actors")
        >>> print(f"Found {len(actors)} actors")
        >>>
        >>> # Cleanup
        >>> client.close()
    """

    def __init__(
        self,
        api_url: str = "https://api.apify.com/v2",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize Apify driver.

        INITIALIZATION ORDER IS CRITICAL (Bug Prevention #0):
        Phase 1: Set custom attributes
        Phase 2: Set parent class attributes
        Phase 3: Create session
        Phase 4: Validate connection

        Args:
            api_url: Apify API base URL (default: https://api.apify.com/v2)
            api_key: API token for authentication (recommended)
            access_token: Alternative authentication token
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts for rate limits (default: 3)
            debug: Enable debug logging (default: False)
            **kwargs: Additional options (reserved)

        Raises:
            AuthenticationError: If credentials are missing or invalid
            ConnectionError: If cannot reach Apify API
        """

        # ===== PHASE 1: Set custom attributes =====
        self.driver_name = "ApifyDriver"
        self.base_api_url = api_url

        # Setup logging (before parent init)
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)
        self.logger = logger

        # ===== PHASE 2: Set parent class attributes =====
        # DO NOT call super().__init__()! Set these manually instead.
        # Parent __init__() calls _validate_connection() which needs self.session.
        self.api_url = api_url
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout or 30
        self.max_retries = max_retries or 3
        self.debug = debug

        # ===== PHASE 3: Create session =====
        # Session creation can now use all attributes set above
        self.session = self._create_session()

        # ===== PHASE 4: Validate connection =====
        # Validation can now use self.session and other attributes
        self._validate_connection()

    @classmethod
    def from_env(cls, **kwargs) -> "ApifyDriver":
        """
        Create driver instance from environment variables.

        Environment variables:
            APIFY_API_TOKEN: API token (required)
            APIFY_API_URL: API base URL (optional, default: https://api.apify.com/v2)

        Returns:
            Configured ApifyDriver instance

        Raises:
            AuthenticationError: If APIFY_API_TOKEN is not set

        Example:
            >>> driver = ApifyDriver.from_env()
            >>> actors = driver.read("/actors")
        """
        api_key = os.getenv("APIFY_API_TOKEN")
        if not api_key:
            raise AuthenticationError(
                "Missing Apify API token. Set APIFY_API_TOKEN environment variable.",
                details={
                    "required_env_vars": ["APIFY_API_TOKEN"],
                    "token_location": "https://console.apify.com/settings/integrations",
                }
            )

        api_url = os.getenv("APIFY_API_URL", "https://api.apify.com/v2")

        return cls(api_url=api_url, api_key=api_key, **kwargs)

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities.

        Returns:
            DriverCapabilities indicating supported operations

        Example:
            >>> capabilities = client.get_capabilities()
            >>> print(f"Write support: {capabilities.write}")
            Write support: True
        """
        return DriverCapabilities(
            read=True,
            write=True,
            update=True,
            delete=True,
            batch_operations=True,
            streaming=True,
            pagination=PaginationStyle.OFFSET,
            query_language=None,  # REST API - no query language
            max_page_size=100,
            supports_transactions=False,
            supports_relationships=True,
        )

    def list_objects(self) -> List[str]:
        """
        List all available resource types.

        Returns:
            List of resource names (actors, datasets, runs, etc.)

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If cannot reach API

        Example:
            >>> resources = client.list_objects()
            >>> print(resources)
            ['actors', 'datasets', 'key-value-stores', 'runs', 'tasks', 'webhooks', ...]
        """
        return [
            "actors",
            "runs",
            "datasets",
            "key-value-stores",
            "request-queues",
            "tasks",
            "webhooks",
            "schedules",
            "builds",
        ]

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get schema/fields for a resource type.

        Args:
            object_name: Name of resource (e.g., "actors", "datasets")

        Returns:
            Dictionary describing available fields and operations

        Raises:
            ObjectNotFoundError: If resource type doesn't exist

        Example:
            >>> fields = client.get_fields("actors")
            >>> print(fields.keys())
            dict_keys(['id', 'name', 'createdAt', 'modifiedAt', ...])
        """
        schemas = {
            "actors": {
                "id": {"type": "string", "description": "Actor ID"},
                "name": {"type": "string", "description": "Actor name"},
                "username": {"type": "string", "description": "Actor owner username"},
                "description": {
                    "type": "string",
                    "description": "Actor description",
                },
                "createdAt": {"type": "datetime", "description": "Creation timestamp"},
                "modifiedAt": {"type": "datetime", "description": "Last modified"},
                "stats": {
                    "type": "object",
                    "description": "Actor statistics",
                },
                "isPublic": {
                    "type": "boolean",
                    "description": "Public visibility flag",
                },
                "isDeprecated": {
                    "type": "boolean",
                    "description": "Deprecation flag",
                },
            },
            "runs": {
                "id": {"type": "string", "description": "Run ID"},
                "actId": {"type": "string", "description": "Actor ID"},
                "actorId": {"type": "string", "description": "Actor ID (alias)"},
                "status": {
                    "type": "string",
                    "description": "Run status (READY, RUNNING, SUCCEEDED, FAILED, ABORTING, ABORTED, TIMING_OUT, TIMED_OUT, RESURRECT_IN_PROGRESS)",
                },
                "defaultDatasetId": {
                    "type": "string",
                    "description": "Dataset ID for results",
                },
                "startedAt": {"type": "datetime", "description": "Start time"},
                "finishedAt": {"type": "datetime", "description": "Finish time"},
                "stats": {
                    "type": "object",
                    "description": "Run statistics",
                },
            },
            "datasets": {
                "id": {"type": "string", "description": "Dataset ID"},
                "name": {"type": "string", "description": "Dataset name"},
                "createdAt": {"type": "datetime", "description": "Creation timestamp"},
                "modifiedAt": {"type": "datetime", "description": "Last modified"},
                "itemCount": {"type": "integer", "description": "Number of items"},
                "stats": {
                    "type": "object",
                    "description": "Dataset statistics",
                },
            },
            "key-value-stores": {
                "id": {"type": "string", "description": "Store ID"},
                "name": {"type": "string", "description": "Store name"},
                "createdAt": {"type": "datetime", "description": "Creation timestamp"},
                "modifiedAt": {"type": "datetime", "description": "Last modified"},
                "itemCount": {"type": "integer", "description": "Number of items"},
            },
        }

        if object_name not in schemas:
            available = list(schemas.keys())
            raise ObjectNotFoundError(
                f"Resource type '{object_name}' not found. Available: {', '.join(available)}",
                details={"requested": object_name, "available": available},
            )

        return schemas[object_name]

    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read operation and return results.

        Args:
            query: API endpoint path (e.g., "/actors", "/datasets/xyz/items")
            limit: Maximum records to return (max: 100, default: None = all)
            offset: Number of records to skip (for pagination, default: 0)

        Returns:
            List of records

        Raises:
            QuerySyntaxError: Invalid endpoint or query format
            RateLimitError: Rate limit exceeded (after retries)
            ConnectionError: Cannot reach API
            AuthenticationError: Invalid credentials

        Example:
            >>> # List all actors
            >>> actors = client.read("/actors", limit=50)
            >>>
            >>> # Paginate through actors
            >>> batch1 = client.read("/actors", limit=50, offset=0)
            >>> batch2 = client.read("/actors", limit=50, offset=50)
            >>>
            >>> # Get dataset items
            >>> items = client.read("/datasets/xyz/items", limit=100)
        """
        # Bug Prevention #4: Validate page size limits
        MAX_PAGE_SIZE = 100
        if limit and limit > MAX_PAGE_SIZE:
            raise ValidationError(
                f"limit cannot exceed {MAX_PAGE_SIZE} (got: {limit})",
                details={
                    "provided": limit,
                    "maximum": MAX_PAGE_SIZE,
                    "parameter": "limit",
                },
            )

        if limit and limit < 1:
            raise ValidationError(
                f"limit must be at least 1 (got: {limit})",
                details={
                    "provided": limit,
                    "minimum": 1,
                    "parameter": "limit",
                },
            )

        # Build request parameters
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset

        # Make request with retry
        try:
            response = self._api_call_with_retry(query, method="GET", params=params)
            return self._parse_response(response)

        except requests.exceptions.Timeout as e:
            raise DriverTimeoutError(
                f"Request to {query} timed out after {self.timeout} seconds",
                details={"endpoint": query, "timeout": self.timeout},
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to read {query}: {str(e)}",
                details={"endpoint": query, "error": str(e)},
            )

    def read_batched(
        self,
        query: str,
        batch_size: int = 100,
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute read operation and yield results in batches (memory-efficient).

        Args:
            query: API endpoint path
            batch_size: Records per batch (max: 100, default: 100)

        Yields:
            Batches of records as lists

        Raises:
            ValidationError: If batch_size exceeds maximum
            RateLimitError: Rate limit exceeded
            ConnectionError: Cannot reach API

        Example:
            >>> total = 0
            >>> for batch in client.read_batched("/datasets/xyz/items", batch_size=50):
            ...     print(f"Processing {len(batch)} records...")
            ...     total += len(batch)
            >>> print(f"Total: {total} records")
        """
        MAX_BATCH_SIZE = 100
        if batch_size > MAX_BATCH_SIZE:
            raise ValidationError(
                f"batch_size cannot exceed {MAX_BATCH_SIZE} (got: {batch_size})",
                details={
                    "provided": batch_size,
                    "maximum": MAX_BATCH_SIZE,
                    "parameter": "batch_size",
                },
            )

        offset = 0
        while True:
            batch = self.read(query, limit=batch_size, offset=offset)
            if not batch:
                break

            yield batch
            offset += len(batch)

            # Stop if we got fewer records than requested (end of data)
            if len(batch) < batch_size:
                break

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource.

        Args:
            object_name: Resource type (e.g., "actors", "tasks")
            data: Resource data

        Returns:
            Created resource with ID

        Raises:
            NotImplementedError: If resource type doesn't support creation
            ValidationError: If data is invalid
            ConnectionError: If cannot reach API

        Example:
            >>> task = client.create("tasks", {
            ...     "actId": "actor-id",
            ...     "name": "my-task"
            ... })
            >>> print(task["id"])
        """
        # Not all resources support creation via API
        if object_name not in ["tasks", "webhooks", "schedules"]:
            raise NotImplementedError(
                f"Creation not supported for resource type '{object_name}'",
                details={"resource_type": object_name},
            )

        try:
            response = self._api_call_with_retry(
                f"/{object_name}",
                method="POST",
                json=data,
            )
            return self._parse_response(response)

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, f"creating {object_name}")

    def update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing resource.

        Args:
            object_name: Resource type
            record_id: Resource ID
            data: Updated fields

        Returns:
            Updated resource

        Raises:
            ObjectNotFoundError: If resource doesn't exist
            ValidationError: If data is invalid
            ConnectionError: If cannot reach API
        """
        try:
            response = self._api_call_with_retry(
                f"/{object_name}/{record_id}",
                method="PUT",
                json=data,
            )
            return self._parse_response(response)

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, f"updating {object_name}/{record_id}")

    def delete(self, object_name: str, record_id: str) -> bool:
        """
        Delete a resource.

        Args:
            object_name: Resource type
            record_id: Resource ID

        Returns:
            True if successful

        Raises:
            ObjectNotFoundError: If resource doesn't exist
            ConnectionError: If cannot reach API

        Note:
            Agents should RARELY generate delete operations!
            Always require explicit user approval.
        """
        try:
            self._api_call_with_retry(
                f"/{object_name}/{record_id}",
                method="DELETE",
            )
            return True

        except requests.exceptions.RequestException as e:
            self._handle_api_error(e, f"deleting {object_name}/{record_id}")

    def close(self):
        """
        Close session and cleanup resources.

        Example:
            >>> client = ApifyDriver.from_env()
            >>> try:
            ...     data = client.read("/actors")
            ... finally:
            ...     client.close()
        """
        if self.session:
            self.session.close()

    # ===== INTERNAL METHODS =====

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication (Bug Prevention #1 & #2).

        Returns:
            Configured requests.Session with auth headers

        Key points:
        - Use EXACT header names (case-sensitive!)
        - Do NOT set Content-Type in session headers
        - Use IF (not ELIF) for multiple auth methods
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
        })
        # NOTE: Do NOT set Content-Type here! requests library handles it automatically

        # Add authentication (use IF, not ELIF - multiple can coexist)
        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"

        if self.api_key:
            # Bug Prevention #1: Use EXACT header name from API docs
            session.headers["Authorization"] = f"Bearer {self.api_key}"

        # Configure retries with exponential backoff (requests library)
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _api_call_with_retry(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make API call with exponential backoff retry on rate limits.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            json: Request body
            **kwargs: Additional request options

        Returns:
            Response object

        Raises:
            AuthenticationError: Invalid credentials
            RateLimitError: Rate limit exceeded after retries
            ConnectionError: Network error
        """
        url = f"{self.api_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                if self.debug:
                    self.logger.debug(f"[DEBUG] {method} {url} params={params}")

                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                    **kwargs
                )

                # Check for rate limit (429)
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 2 ** attempt))

                    if attempt < self.max_retries - 1:
                        if self.debug:
                            self.logger.debug(
                                f"[DEBUG] Rate limited. Retrying in {retry_after}s..."
                            )
                        time.sleep(retry_after)
                        continue
                    else:
                        raise RateLimitError(
                            f"Rate limit exceeded. Retry after {retry_after} seconds.",
                            details={
                                "retry_after": retry_after,
                                "endpoint": endpoint,
                                "attempts": self.max_retries,
                            },
                        )

                # Check other HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid Apify API token. Check APIFY_API_TOKEN environment variable.",
                        details={"status_code": 401, "endpoint": endpoint},
                    )

                if response.status_code == 404:
                    raise ObjectNotFoundError(
                        f"Resource not found: {endpoint}",
                        details={"status_code": 404, "endpoint": endpoint},
                    )

                if response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", response.text)
                    except ValueError:
                        error_msg = response.text[:500]

                    raise QuerySyntaxError(
                        f"API error {response.status_code}: {error_msg}",
                        details={
                            "status_code": response.status_code,
                            "endpoint": endpoint,
                            "error": error_msg,
                        },
                    )

                response.raise_for_status()
                return response

            except requests.exceptions.Timeout:
                raise
            except requests.exceptions.RequestException:
                raise

        raise ConnectionError(f"Failed to connect to {endpoint}")

    def _parse_response(self, response: requests.Response) -> Any:
        """
        Parse API response and extract data (Bug Prevention #3).

        Handles different response formats:
        - Direct arrays: [{"id": 1}, {"id": 2}]
        - Wrapped objects: {"items": [...]}
        - Metadata: {"data": {"items": [...], "total": 100}}

        Args:
            response: HTTP response object

        Returns:
            Parsed data (list or dict)

        Raises:
            ConnectionError: Invalid JSON response
        """
        try:
            data = response.json()
        except ValueError as e:
            raise ConnectionError(
                f"Invalid JSON response from API",
                details={
                    "status_code": response.status_code,
                    "content": response.text[:500],
                    "error": str(e),
                },
            )

        # Handle direct array responses
        if isinstance(data, list):
            return data

        # Handle object-wrapped responses
        if isinstance(data, dict):
            # Bug Prevention #3: Try all known field names (case-sensitive!)
            # Order: documented field first, then common variations
            records = (
                data.get("items") or  # Primary data field from Apify docs
                data.get("Items") or
                data.get("data") or
                data.get("Data") or
                data.get("results") or
                data.get("Results") or
                data.get("records") or
                data.get("Records") or
                []
            )

            # Ensure we return a list
            if isinstance(records, list):
                return records
            elif records is not None:
                return [records]  # Wrap single object
            else:
                # If no data field found, return the response as-is
                return data

        return []

    def _handle_api_error(self, error: Exception, context: str = ""):
        """
        Convert exceptions to structured driver exceptions.

        Args:
            error: Exception from requests library
            context: Context description

        Raises:
            Appropriate DriverError subclass
        """
        if isinstance(error, requests.exceptions.HTTPError):
            status_code = error.response.status_code
            if status_code == 401:
                raise AuthenticationError(
                    f"Invalid credentials: {context}",
                    details={"status_code": 401, "context": context},
                )
            elif status_code == 404:
                raise ObjectNotFoundError(
                    f"Resource not found: {context}",
                    details={"status_code": 404, "context": context},
                )
            elif status_code == 429:
                raise RateLimitError(
                    f"Rate limit exceeded: {context}",
                    details={"status_code": 429, "context": context},
                )

        raise ConnectionError(
            f"API error during {context}: {str(error)}",
            details={"error": str(error), "context": context},
        )

    def _validate_connection(self):
        """
        Validate connection at init time (fail fast!).

        Raises:
            AuthenticationError: Invalid credentials
            ConnectionError: Cannot reach API
        """
        if not self.api_key and not self.access_token:
            raise AuthenticationError(
                "Missing authentication. Set api_key or access_token parameter, or APIFY_API_TOKEN environment variable.",
                details={
                    "required": "api_key or access_token",
                    "env_var": "APIFY_API_TOKEN",
                },
            )

        try:
            # Quick validation: GET /acts (actors endpoint)
            response = self.session.get(
                f"{self.api_url}/acts",
                timeout=self.timeout,
                params={"limit": 1},
            )

            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Apify API token. Check APIFY_API_TOKEN environment variable.",
                    details={"api_url": self.api_url},
                )

            if response.status_code >= 500:
                raise ConnectionError(
                    f"Apify API server error: HTTP {response.status_code}",
                    details={"api_url": self.api_url, "status_code": response.status_code},
                )

            response.raise_for_status()

        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"Cannot reach Apify API (timeout after {self.timeout}s): {self.api_url}",
                details={"api_url": self.api_url, "timeout": self.timeout},
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot reach Apify API: {self.api_url}",
                details={"api_url": self.api_url},
            )
