"""
PostHog Python Driver

A production-ready Python driver for the PostHog API.

Features:
- Full CRUD operations on dashboards, datasets, batch exports, and more
- Cursor-based pagination with automatic limit/offset handling
- Automatic retry on rate limits with exponential backoff
- Structured error handling with actionable suggestions
- Debug mode for troubleshooting API calls
- Support for both cloud (US/EU) and self-hosted PostHog instances

Authentication:
- Personal API Key for private endpoints (required for CRUD operations)
- Project API Key for public endpoints (optional, for event capture)

Rate Limits:
- CRUD operations: 480 requests/minute, 4800 requests/hour
- Query endpoint: 2400 requests/hour
- Public POST endpoints: Unlimited

Usage:
    from posthog_driver import PostHogDriver

    # Initialize from environment variables
    driver = PostHogDriver.from_env()

    # Discover available objects
    objects = driver.list_objects()

    # Get field schema
    fields = driver.get_fields("dashboards")

    # Execute read query
    results = driver.read("SELECT * FROM dashboards LIMIT 10")

    # Create a new dashboard
    dashboard = driver.create("dashboards", {
        "name": "My Dashboard",
        "description": "Test dashboard"
    })

    # Cleanup
    driver.close()
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Handle both package and standalone imports
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
        TimeoutError,
    )
except ImportError:
    # Running as standalone script
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
        TimeoutError,
    )


class PostHogDriver(BaseDriver):
    """
    PostHog Python Driver

    Provides comprehensive access to PostHog API with automatic pagination,
    rate limiting, and error handling.

    Attributes:
        api_url: Base URL for PostHog API
        api_key: Personal API key for authentication
        project_id: PostHog project ID
        timeout: Request timeout in seconds
        max_retries: Number of retry attempts for rate limiting
        debug: Enable debug logging

    Example:
        >>> driver = PostHogDriver.from_env()
        >>> dashboards = driver.read("SELECT id, name FROM dashboards")
        >>> for dashboard in dashboards:
        ...     print(dashboard['name'])
        >>> driver.close()
    """

    # Available objects/resources
    OBJECTS = [
        "batch_exports",
        "dashboards",
        "datasets",
        "dataset_items",
        "desktop_recordings",
        "error_tracking",
        "endpoints",
        "persons",
        "events",
        "feature_flags",
    ]

    def __init__(
        self,
        api_url: str = "https://app.posthog.com/api",
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize PostHog driver.

        CRITICAL: Follows 4-phase initialization order:
        1. Phase 1: Custom attributes (project_id, logger)
        2. Phase 2: Parent attributes (api_url, api_key, etc.)
        3. Phase 3: Create session
        4. Phase 4: Validate connection

        Args:
            api_url: PostHog API base URL
                Default: https://app.posthog.com/api
                EU: https://eu.posthog.com/api
                Self-hosted: https://your-instance.com/api
            api_key: Personal API key for authentication
                Can be loaded from POSTHOG_API_KEY environment variable
            project_id: PostHog project ID (optional, can be inferred from API)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Retry attempts on rate limit (default: 3)
            debug: Enable debug logging (default: False)

        Raises:
            AuthenticationError: If API key is invalid or missing
            ConnectionError: If cannot reach PostHog API

        Example:
            >>> # Load from environment
            >>> driver = PostHogDriver.from_env()

            >>> # Or explicit credentials
            >>> driver = PostHogDriver(
            ...     api_url="https://eu.posthog.com/api",
            ...     api_key="your_personal_api_key"
            ... )
        """

        # ===== PHASE 1: Set custom attributes =====
        self.project_id = project_id
        self.driver_name = "PostHogDriver"

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)

        self.logger = logger

        # ===== PHASE 2: Set parent class attributes =====
        # DO NOT call super().__init__()! Set these manually.
        # This must happen BEFORE _create_session() so session can use them.
        self.api_url = api_url or "https://app.posthog.com/api"
        self.api_key = api_key
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
    def from_env(cls, **kwargs) -> "PostHogDriver":
        """
        Create driver instance from environment variables.

        Environment variables:
            POSTHOG_API_KEY: Personal API key (required)
            POSTHOG_API_URL: API base URL (optional, default: https://app.posthog.com/api)
            POSTHOG_PROJECT_ID: Project ID (optional)

        Args:
            **kwargs: Additional arguments passed to __init__

        Returns:
            Configured PostHogDriver instance

        Raises:
            AuthenticationError: If POSTHOG_API_KEY is not set

        Example:
            >>> driver = PostHogDriver.from_env()
            >>> objects = driver.list_objects()

        To use:
            1. Set environment variable: export POSTHOG_API_KEY=your_api_key
            2. Create driver: driver = PostHogDriver.from_env()
        """
        api_key = os.getenv("POSTHOG_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing PostHog API key. Set POSTHOG_API_KEY environment variable.",
                details={
                    "required_env_vars": ["POSTHOG_API_KEY"],
                    "optional_env_vars": ["POSTHOG_API_URL", "POSTHOG_PROJECT_ID"],
                    "suggestion": "export POSTHOG_API_KEY=your_personal_api_key",
                },
            )

        api_url = os.getenv("POSTHOG_API_URL", "https://app.posthog.com/api")
        project_id = os.getenv("POSTHOG_PROJECT_ID")

        return cls(api_url=api_url, api_key=api_key, project_id=project_id, **kwargs)

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities.

        PostHog driver supports:
        - Full CRUD operations on most resources
        - Cursor-based pagination
        - Batch operations
        - Server-Sent Events streaming

        Returns:
            DriverCapabilities with feature flags

        Example:
            >>> caps = driver.get_capabilities()
            >>> if caps.write:
            ...     print("Can create new resources")
        """
        return DriverCapabilities(
            read=True,
            write=True,
            update=True,
            delete=True,
            batch_operations=True,
            streaming=True,
            pagination=PaginationStyle.CURSOR,
            query_language=None,  # REST API, no query language
            max_page_size=100,
            supports_transactions=False,
            supports_relationships=True,
        )

    def list_objects(self) -> List[str]:
        """
        List available objects/resources in PostHog.

        Returns:
            List of resource names

        Example:
            >>> objects = driver.list_objects()
            >>> for obj in objects:
            ...     print(obj)
            batch_exports
            dashboards
            datasets
            ...
        """
        return self.OBJECTS

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get field schema for a PostHog resource.

        For each object, returns a schema describing:
        - Field name and type
        - Whether field is required/nullable
        - Maximum length (for strings)
        - Human-readable label

        Args:
            object_name: Name of the resource (e.g., "dashboards", "datasets")

        Returns:
            Dictionary mapping field names to field metadata

        Raises:
            ObjectNotFoundError: If object_name is not recognized

        Example:
            >>> fields = driver.get_fields("dashboards")
            >>> if "name" in fields:
            ...     print(f"Name field type: {fields['name']['type']}")
            {'type': 'string', 'required': True, ...}
        """
        if object_name not in self.OBJECTS:
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found in PostHog API",
                details={
                    "requested": object_name,
                    "available": self.OBJECTS,
                    "suggestion": f"Use list_objects() to see available resources",
                },
            )

        # Common fields across most PostHog resources
        common_fields = {
            "id": {
                "type": "string",
                "label": "ID",
                "required": False,
                "nullable": False,
                "description": "Unique identifier",
            },
            "created_at": {
                "type": "datetime",
                "label": "Created At",
                "required": False,
                "nullable": False,
                "description": "Creation timestamp",
            },
            "updated_at": {
                "type": "datetime",
                "label": "Updated At",
                "required": False,
                "nullable": False,
                "description": "Last update timestamp",
            },
        }

        # Resource-specific fields
        resource_fields = {
            "batch_exports": {
                **common_fields,
                "name": {
                    "type": "string",
                    "label": "Name",
                    "required": True,
                    "nullable": False,
                    "max_length": 255,
                    "description": "Batch export name",
                },
                "destination": {
                    "type": "object",
                    "label": "Destination",
                    "required": True,
                    "nullable": False,
                    "description": "Export destination configuration",
                },
                "status": {
                    "type": "string",
                    "label": "Status",
                    "required": False,
                    "nullable": False,
                    "enum": ["running", "paused", "completed", "failed"],
                    "description": "Export status",
                },
            },
            "dashboards": {
                **common_fields,
                "name": {
                    "type": "string",
                    "label": "Name",
                    "required": True,
                    "nullable": False,
                    "max_length": 255,
                    "description": "Dashboard name",
                },
                "description": {
                    "type": "string",
                    "label": "Description",
                    "required": False,
                    "nullable": True,
                    "description": "Dashboard description",
                },
                "tiles": {
                    "type": "array",
                    "label": "Tiles",
                    "required": False,
                    "nullable": False,
                    "description": "Dashboard tiles/visualizations",
                },
            },
            "datasets": {
                **common_fields,
                "name": {
                    "type": "string",
                    "label": "Name",
                    "required": True,
                    "nullable": False,
                    "max_length": 255,
                    "description": "Dataset name",
                },
                "description": {
                    "type": "string",
                    "label": "Description",
                    "required": False,
                    "nullable": True,
                    "description": "Dataset description",
                },
            },
            "dataset_items": {
                **common_fields,
                "dataset_id": {
                    "type": "string",
                    "label": "Dataset ID",
                    "required": True,
                    "nullable": False,
                    "description": "Parent dataset ID",
                },
                "value": {
                    "type": "any",
                    "label": "Value",
                    "required": True,
                    "nullable": False,
                    "description": "Item value",
                },
            },
            "persons": {
                **common_fields,
                "properties": {
                    "type": "object",
                    "label": "Properties",
                    "required": False,
                    "nullable": True,
                    "description": "Person properties",
                },
            },
            "events": {
                **common_fields,
                "event": {
                    "type": "string",
                    "label": "Event",
                    "required": True,
                    "nullable": False,
                    "description": "Event name",
                },
                "properties": {
                    "type": "object",
                    "label": "Properties",
                    "required": False,
                    "nullable": True,
                    "description": "Event properties",
                },
            },
            "feature_flags": {
                **common_fields,
                "key": {
                    "type": "string",
                    "label": "Key",
                    "required": True,
                    "nullable": False,
                    "description": "Feature flag key",
                },
                "active": {
                    "type": "boolean",
                    "label": "Active",
                    "required": False,
                    "nullable": False,
                    "description": "Is feature flag active",
                },
            },
            "desktop_recordings": {
                **common_fields,
                "name": {
                    "type": "string",
                    "label": "Name",
                    "required": False,
                    "nullable": True,
                    "description": "Recording name",
                },
            },
            "error_tracking": {
                **common_fields,
                "fingerprint": {
                    "type": "string",
                    "label": "Fingerprint",
                    "required": True,
                    "nullable": False,
                    "description": "Error fingerprint",
                },
            },
            "endpoints": {
                **common_fields,
                "name": {
                    "type": "string",
                    "label": "Name",
                    "required": True,
                    "nullable": False,
                    "description": "Endpoint/materialized query name",
                },
                "query": {
                    "type": "object",
                    "label": "Query",
                    "required": True,
                    "nullable": False,
                    "description": "Query definition",
                },
            },
        }

        return resource_fields.get(object_name, common_fields)

    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results.

        For PostHog, the query parameter is used as an endpoint path/selector.
        Pagination is handled automatically.

        Args:
            query: Endpoint path or resource selector (e.g., "/dashboards", "/datasets")
                   Can also use full endpoint like "/environments/{project_id}/dashboards/"
            limit: Maximum records to return (max: 100)
            offset: Number of records to skip (for pagination)

        Returns:
            List of records

        Raises:
            QuerySyntaxError: If endpoint is invalid
            RateLimitError: If rate limit exceeded
            ObjectNotFoundError: If resource not found

        Example:
            >>> # Get all dashboards
            >>> dashboards = driver.read("/dashboards")

            >>> # Get dashboards with pagination
            >>> dashboards = driver.read("/dashboards", limit=50, offset=0)

            >>> # Validate returned data
            >>> for dashboard in dashboards:
            ...     print(dashboard['name'])
        """
        if limit and limit > 100:
            raise ValidationError(
                f"limit cannot exceed 100 (got: {limit})",
                details={
                    "provided": limit,
                    "maximum": 100,
                    "parameter": "limit",
                    "suggestion": "Use limit <= 100",
                },
            )

        if limit is None:
            limit = 50  # Safe default

        # Build request URL
        endpoint = query.lstrip("/")
        if not endpoint.startswith("environments/"):
            # Auto-inject project_id if needed
            if self.project_id:
                endpoint = f"environments/{self.project_id}/{endpoint}"
            else:
                endpoint = f"environments/default/{endpoint}"

        url = urljoin(self.api_url, endpoint)

        # Build query parameters
        params = {"limit": limit}
        if offset is not None:
            params["offset"] = offset

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request to {endpoint} timed out after {self.timeout} seconds",
                details={
                    "timeout": self.timeout,
                    "endpoint": endpoint,
                    "suggestion": "Try increasing timeout or reducing query scope",
                },
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot reach PostHog API at {self.api_url}",
                details={
                    "api_url": self.api_url,
                    "error": str(e),
                    "suggestion": "Check your internet connection or api_url",
                },
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid PostHog API key. Check your credentials.",
                    details={
                        "status_code": 401,
                        "api_url": self.api_url,
                        "suggestion": "Verify POSTHOG_API_KEY is correct",
                    },
                )
            elif response.status_code == 404:
                raise ObjectNotFoundError(
                    f"Resource '{endpoint}' not found",
                    details={
                        "endpoint": endpoint,
                        "available": self.OBJECTS,
                        "suggestion": "Use list_objects() to see available resources",
                    },
                )
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(
                    f"PostHog API rate limit exceeded. Retry after {retry_after} seconds.",
                    details={
                        "retry_after": retry_after,
                        "suggestion": "Wait and retry, or reduce request frequency",
                    },
                )
            raise QuerySyntaxError(
                f"Query error: {response.status_code} {response.reason}",
                details={
                    "status_code": response.status_code,
                    "error": response.text[:500],
                    "endpoint": endpoint,
                },
            )

        # Parse response
        return self._parse_response(response)

    def read_batched(
        self, query: str, batch_size: int = 1000
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute query and yield results in batches (memory-efficient).

        Args:
            query: Endpoint path (e.g., "/dashboards")
            batch_size: Records per batch (max: 100)

        Yields:
            Batches of records as lists of dictionaries

        Raises:
            ValidationError: If batch_size exceeds API limit

        Example:
            >>> for batch in driver.read_batched("/events", batch_size=100):
            ...     process_batch(batch)
            ...     print(f"Processed {len(batch)} records")
        """
        if batch_size > 100:
            raise ValidationError(
                f"batch_size cannot exceed 100 (got: {batch_size})",
                details={
                    "provided": batch_size,
                    "maximum": 100,
                    "suggestion": "Use batch_size <= 100",
                },
            )

        offset = 0
        while True:
            batch = self.read(query, limit=batch_size, offset=offset)
            if not batch:
                break

            yield batch
            offset += batch_size

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new resource.

        Args:
            object_name: Resource type (e.g., "dashboards", "datasets")
            data: Resource data as dictionary

        Returns:
            Created resource with ID

        Raises:
            NotImplementedError: If resource doesn't support creation
            ValidationError: If data is invalid
            ObjectNotFoundError: If resource type not found

        Example:
            >>> dashboard = driver.create("dashboards", {
            ...     "name": "My Dashboard",
            ...     "description": "Test dashboard"
            ... })
            >>> print(dashboard['id'])
        """
        if object_name not in self.OBJECTS:
            raise ObjectNotFoundError(
                f"Object type '{object_name}' not found",
                details={
                    "requested": object_name,
                    "available": self.OBJECTS,
                },
            )

        # Build endpoint URL
        if self.project_id:
            endpoint = f"environments/{self.project_id}/{object_name}/"
        else:
            endpoint = f"environments/default/{object_name}/"

        url = urljoin(self.api_url, endpoint)

        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                error_msg = response.json().get("detail", "Invalid request")
                raise ValidationError(
                    f"Validation failed: {error_msg}",
                    details={
                        "object": object_name,
                        "status_code": 400,
                        "error": error_msg,
                    },
                )
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid PostHog API key",
                    details={"status_code": 401},
                )
            raise

        return response.json()

    def update(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing resource.

        Args:
            object_name: Resource type (e.g., "dashboards")
            record_id: Resource ID to update
            data: Fields to update

        Returns:
            Updated resource

        Raises:
            ObjectNotFoundError: If resource doesn't exist
            ValidationError: If data is invalid

        Example:
            >>> updated = driver.update("dashboards", "123", {
            ...     "name": "Updated Name"
            ... })
        """
        if object_name not in self.OBJECTS:
            raise ObjectNotFoundError(
                f"Object type '{object_name}' not found",
                details={"requested": object_name, "available": self.OBJECTS},
            )

        # Build endpoint URL
        if self.project_id:
            endpoint = f"environments/{self.project_id}/{object_name}/{record_id}/"
        else:
            endpoint = f"environments/default/{object_name}/{record_id}/"

        url = urljoin(self.api_url, endpoint)

        try:
            response = self.session.patch(url, json=data, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ObjectNotFoundError(
                    f"Resource '{object_name}/{record_id}' not found",
                    details={
                        "object": object_name,
                        "record_id": record_id,
                        "status_code": 404,
                    },
                )
            raise

        return response.json()

    def delete(self, object_name: str, record_id: str) -> bool:
        """
        Delete a resource.

        WARNING: This operation cannot be undone. Always require explicit user approval.

        Args:
            object_name: Resource type
            record_id: Resource ID to delete

        Returns:
            True if successful

        Raises:
            ObjectNotFoundError: If resource doesn't exist

        Example:
            >>> success = driver.delete("dashboards", "123")
            >>> print(f"Deleted: {success}")
        """
        if object_name not in self.OBJECTS:
            raise ObjectNotFoundError(
                f"Object type '{object_name}' not found",
                details={"requested": object_name, "available": self.OBJECTS},
            )

        # Build endpoint URL
        if self.project_id:
            endpoint = f"environments/{self.project_id}/{object_name}/{record_id}/"
        else:
            endpoint = f"environments/default/{object_name}/{record_id}/"

        url = urljoin(self.api_url, endpoint)

        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                raise ObjectNotFoundError(
                    f"Resource '{object_name}/{record_id}' not found",
                    details={
                        "object": object_name,
                        "record_id": record_id,
                        "status_code": 404,
                    },
                )
            raise

    def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Call a PostHog API endpoint directly (low-level access).

        Args:
            endpoint: API endpoint path (e.g., "/dashboards", "/query")
            method: HTTP method (GET, POST, PATCH, DELETE)
            params: URL query parameters
            data: Request body (for POST/PATCH)
            **kwargs: Additional request options

        Returns:
            Response data

        Example:
            >>> result = driver.call_endpoint(
            ...     endpoint="/dashboards",
            ...     method="GET",
            ...     params={"limit": 50}
            ... )
        """
        url = urljoin(self.api_url, endpoint.lstrip("/"))

        response = self.session.request(
            method, url, params=params, json=data, timeout=self.timeout, **kwargs
        )
        response.raise_for_status()

        return response.json()

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status (if available in response headers).

        Returns:
            Dictionary with rate limit information (when available)

        Example:
            >>> status = driver.get_rate_limit_status()
            >>> if status.get("remaining"):
            ...     print(f"Requests remaining: {status['remaining']}")
        """
        # PostHog doesn't provide rate limit headers in all responses
        # This is a placeholder for when headers are available
        return {
            "remaining": None,
            "limit": None,
            "reset_at": None,
            "retry_after": None,
        }

    def close(self):
        """
        Close session and cleanup resources.

        Example:
            >>> driver = PostHogDriver.from_env()
            >>> try:
            ...     results = driver.read("/dashboards")
            ... finally:
            ...     driver.close()
        """
        if self.session:
            self.session.close()
            self.logger.debug("PostHog driver session closed")

    # ===== PRIVATE HELPER METHODS =====

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication and retry strategy.

        BUG PREVENTION #1 & #2: Authentication headers

        - Uses EXACT header name: Authorization
        - Bearer token format for Personal API Key
        - Does NOT set Content-Type in headers (handled by requests)
        - Configures automatic retry on rate limits

        Returns:
            Configured requests.Session

        NOTE: This method is called during Phase 3 of initialization,
        after parent attributes are set but before validation.
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
            }
        )
        # NOTE: Do NOT set Content-Type here! (requests library handles it)

        # Add authentication (use IF, not ELIF - multiple can coexist)
        if self.api_key:
            # BUG PREVENTION #1: EXACT header name "Authorization"
            session.headers["Authorization"] = f"Bearer {self.api_key}"

        # Configure retry strategy for rate limits
        if self.max_retries > 0:
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s, 8s
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

        if self.debug:
            self.logger.debug(f"Session created with retry strategy: {retry_strategy}")

        return session

    def _parse_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        Parse API response and extract data records.

        BUG PREVENTION #3: Response parsing

        Handles different response formats:
        - Direct arrays: [{"id": 1}, {"id": 2}]
        - Wrapped objects: {"results": [...], "count": 100}
        - Alternative field names: "data", "items"

        Args:
            response: HTTP response from API

        Returns:
            List of records

        Raises:
            ConnectionError: If response is not valid JSON
        """
        try:
            data = response.json()
        except ValueError as e:
            raise ConnectionError(
                f"Invalid JSON response from PostHog API",
                details={
                    "status_code": response.status_code,
                    "content": response.text[:500],
                    "error": str(e),
                },
            )

        # Handle direct array responses
        if isinstance(data, list):
            if self.debug:
                self.logger.debug(f"Parsed array response with {len(data)} records")
            return data

        # Handle object-wrapped responses
        if isinstance(data, dict):
            # BUG PREVENTION #3: Try all known field names (case-sensitive!)
            # Primary field first, then common alternatives
            records = (
                data.get("results")
                or data.get("data")
                or data.get("items")
                or data.get("Results")
                or data.get("Data")
                or data.get("Items")
                or []
            )

            # Ensure we return a list
            if isinstance(records, list):
                if self.debug:
                    self.logger.debug(f"Parsed wrapped response with {len(records)} records")
                return records
            elif records is not None:
                # Single object, wrap in list
                return [records]
            else:
                return []

        # Unknown format
        if self.debug:
            self.logger.debug(f"Unknown response format: {type(data)}")
        return []

    def _validate_connection(self):
        """
        Validate connection at __init__ time (fail fast!).

        Tests that:
        1. API key is present
        2. API is reachable
        3. Credentials are valid

        Called during Phase 4 of initialization, after session is created.

        Raises:
            AuthenticationError: If credentials invalid
            ConnectionError: If API unreachable
        """
        if not self.api_key:
            raise AuthenticationError(
                "PostHog API key is required. Set POSTHOG_API_KEY environment variable.",
                details={
                    "required_env_vars": ["POSTHOG_API_KEY"],
                    "suggestion": "export POSTHOG_API_KEY=your_personal_api_key",
                },
            )

        try:
            # Test connection by making a simple list request
            test_url = urljoin(self.api_url, "environments/")
            response = self.session.get(test_url, timeout=self.timeout)

            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid PostHog API key. Check your credentials.",
                    details={
                        "api_url": self.api_url,
                        "status_code": 401,
                        "suggestion": "Verify POSTHOG_API_KEY is correct and has required permissions",
                    },
                )

            response.raise_for_status()

            if self.debug:
                self.logger.debug("PostHog API connection validated successfully")

        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"PostHog API connection timed out. Cannot reach {self.api_url}",
                details={
                    "api_url": self.api_url,
                    "timeout": self.timeout,
                    "suggestion": "Check your internet connection or try again later",
                },
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot reach PostHog API at {self.api_url}",
                details={
                    "api_url": self.api_url,
                    "error": str(e),
                    "suggestion": "Check network connectivity and api_url configuration",
                },
            )
