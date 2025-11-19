"""
Amplitude Analytics Driver - Production Implementation

This driver provides access to Amplitude's Batch Event Upload, Identify, and Export APIs.

Key Features:
- Event ingestion via Batch Event Upload API (up to 2000 events per batch)
- User property updates via Identify API
- Event export via Export API
- Automatic retry on rate limits with exponential backoff
- Comprehensive error handling with structured exceptions

Authentication:
- API Key passed in request body
- Environment variable: AMPLITUDE_API_KEY

Usage:
    >>> from amplitude import AmplitudeDriver
    >>> client = AmplitudeDriver.from_env()
    >>> # Upload events
    >>> result = client.create("events", {
    ...     "user_id": "user123",
    ...     "event_type": "page_view",
    ...     "event_properties": {"page": "/home"}
    ... })
"""

import logging
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Iterator
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Try package imports first, fallback to standalone
try:
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


# ============================================================================
# Data Classes
# ============================================================================


class PaginationStyle(Enum):
    """How the driver handles pagination."""

    NONE = "none"
    OFFSET = "offset"
    CURSOR = "cursor"
    PAGE_NUMBER = "page"


@dataclass
class DriverCapabilities:
    """What the driver can do."""

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


# ============================================================================
# Main Driver Class
# ============================================================================


class AmplitudeDriver:
    """
    Amplitude Analytics driver for event ingestion and user property management.

    This driver implements core Amplitude APIs:
    - Batch Event Upload: Ingest events (POST /batch)
    - Identify: Update user properties (POST /identify)
    - Export: Export historical events (GET /api/2/export)

    Initialization follows strict 4-phase pattern:
    1. Set custom attributes
    2. Set parent class attributes
    3. Create session
    4. Validate connection

    Example:
        >>> driver = AmplitudeDriver.from_env()
        >>> events = [{
        ...     "user_id": "user123",
        ...     "event_type": "signup",
        ...     "time": 1234567890000
        ... }]
        >>> result = driver.create_batch(events)
    """

    # ========================================================================
    # Initialization
    # ========================================================================

    def __init__(
        self,
        base_url: str = "https://api2.amplitude.com",
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs,
    ):
        """
        Initialize Amplitude driver.

        CRITICAL: Initialization follows strict 4-phase order.
        See: driver_design_v2.md Section 6: Bug Prevention Pattern #0

        Args:
            base_url: API base URL (default: https://api2.amplitude.com)
            api_key: Amplitude API key
            access_token: Alternative authentication token (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts for rate limiting (default: 3)
            debug: Enable debug logging (default: False)
            **kwargs: Additional driver-specific options

        Raises:
            AuthenticationError: If credentials are missing or invalid
            ConnectionError: If cannot reach API

        Example:
            >>> driver = AmplitudeDriver(
            ...     api_key="YOUR_API_KEY",
            ...     debug=True
            ... )
        """

        # ====================================================================
        # PHASE 1: Set custom attributes
        # ====================================================================
        self.driver_name = "AmplitudeDriver"

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)
        self.logger = logger

        # ====================================================================
        # PHASE 2: Set parent class attributes
        # ====================================================================
        # DO NOT call super().__init__()! Set these manually instead.
        # Must happen BEFORE _create_session() so session can use them.
        self.base_url = base_url
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout or 30
        self.max_retries = max_retries or 3
        self.debug = debug

        # ====================================================================
        # PHASE 3: Create session
        # ====================================================================
        # Session creation can now use all attributes set above
        self.session = self._create_session()

        # ====================================================================
        # PHASE 4: Validate connection
        # ====================================================================
        # Validation can now use self.session and other attributes
        self._validate_connection()

    @classmethod
    def from_env(cls, **kwargs) -> "AmplitudeDriver":
        """
        Create driver instance from environment variables.

        Environment variables:
            AMPLITUDE_API_KEY: Amplitude project API key (required)
            AMPLITUDE_BASE_URL: API base URL (optional, defaults to standard endpoint)
            AMPLITUDE_DEBUG: Enable debug mode (optional, defaults to False)

        Args:
            **kwargs: Additional arguments passed to __init__

        Returns:
            Configured driver instance

        Raises:
            AuthenticationError: If AMPLITUDE_API_KEY is not set

        Example:
            >>> # Set env vars
            >>> os.environ["AMPLITUDE_API_KEY"] = "abc123..."
            >>> # Create driver
            >>> driver = AmplitudeDriver.from_env()
        """
        api_key = os.getenv("AMPLITUDE_API_KEY")
        if not api_key:
            raise AuthenticationError(
                "Missing Amplitude API key. Set AMPLITUDE_API_KEY environment variable.",
                details={
                    "required_env_vars": ["AMPLITUDE_API_KEY"],
                    "suggestion": "export AMPLITUDE_API_KEY='your_api_key'",
                },
            )

        base_url = os.getenv(
            "AMPLITUDE_BASE_URL", "https://api2.amplitude.com"
        )
        debug = os.getenv("AMPLITUDE_DEBUG", "false").lower() == "true"

        return cls(
            base_url=base_url,
            api_key=api_key,
            debug=debug,
            **kwargs,
        )

    # ========================================================================
    # Core Interface (BaseDriver contract)
    # ========================================================================

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities so agent knows what it can do.

        Returns:
            DriverCapabilities with boolean flags for features

        Example:
            >>> capabilities = client.get_capabilities()
            >>> if capabilities.batch_operations:
            ...     print("Batch operations supported")
        """
        return DriverCapabilities(
            read=True,
            write=True,
            update=True,
            delete=False,
            batch_operations=True,
            streaming=False,
            pagination=PaginationStyle.NONE,
            query_language=None,
            max_page_size=2000,
            supports_transactions=False,
            supports_relationships=False,
        )

    def list_objects(self) -> List[str]:
        """
        Discover all available objects/resources.

        Returns:
            List of object names (e.g., ["events", "users", "annotations"])

        Example:
            >>> objects = client.list_objects()
            >>> print(objects)
            ['events', 'users', 'user_properties', 'annotations']
        """
        return [
            "events",
            "users",
            "user_properties",
            "annotations",
        ]

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete field schema for an object.

        Args:
            object_name: Name of object (case-sensitive!)

        Returns:
            Dictionary with field definitions for the object

        Raises:
            ObjectNotFoundError: If object doesn't exist

        Example:
            >>> fields = client.get_fields("events")
            >>> print(fields.keys())
            dict_keys(['user_id', 'device_id', 'event_type', ...])
        """
        objects_schema = {
            "events": {
                "user_id": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "label": "User ID",
                    "description": "Unique user identifier (min 5 chars, required if device_id missing)",
                },
                "device_id": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "label": "Device ID",
                    "description": "Device identifier (min 5 chars, required if user_id missing)",
                },
                "event_type": {
                    "type": "string",
                    "required": True,
                    "nullable": False,
                    "label": "Event Type",
                    "description": "Unique identifier for the event",
                },
                "time": {
                    "type": "integer",
                    "required": False,
                    "nullable": True,
                    "label": "Timestamp",
                    "description": "Event timestamp in milliseconds since epoch",
                },
                "event_properties": {
                    "type": "object",
                    "required": False,
                    "nullable": True,
                    "label": "Event Properties",
                    "description": "Dictionary of event-specific properties",
                },
                "user_properties": {
                    "type": "object",
                    "required": False,
                    "nullable": True,
                    "label": "User Properties",
                    "description": "Dictionary of user properties to update",
                },
                "groups": {
                    "type": "object",
                    "required": False,
                    "nullable": True,
                    "label": "Groups",
                    "description": "Dictionary of group identifiers (requires Accounts add-on)",
                },
                "session_id": {
                    "type": "integer",
                    "required": False,
                    "nullable": True,
                    "label": "Session ID",
                    "description": "Session start time in milliseconds since epoch",
                },
                "insert_id": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "label": "Insert ID",
                    "description": "Unique identifier for deduplication (within 7 days)",
                },
            },
            "users": {
                "user_id": {
                    "type": "string",
                    "required": True,
                    "nullable": False,
                    "label": "User ID",
                    "description": "Unique user identifier",
                },
                "device_id": {
                    "type": "string",
                    "required": False,
                    "nullable": True,
                    "label": "Device ID",
                    "description": "Device identifier to associate with user",
                },
                "user_properties": {
                    "type": "object",
                    "required": False,
                    "nullable": True,
                    "label": "User Properties",
                    "description": "Properties to update for the user",
                },
            },
        }

        if object_name not in objects_schema:
            available = list(objects_schema.keys())
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found. Available objects: {', '.join(available)}",
                details={
                    "requested": object_name,
                    "available": available,
                },
            )

        return objects_schema[object_name]

    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query.

        For Amplitude, this exports historical event data using the Export API.

        Args:
            query: Query specification (format: "start=YYYYMMDDTHH&end=YYYYMMDDTHH")
            limit: Maximum number of records (not used for Export API)
            offset: Number of records to skip (not used for Export API)

        Returns:
            List of event dictionaries

        Raises:
            QuerySyntaxError: If query format is invalid
            RateLimitError: If API rate limit exceeded
            ConnectionError: If API is unreachable

        Example:
            >>> # Export events for a date range
            >>> events = client.read("start=20250101T00&end=20250101T23")
            >>> print(f"Exported {len(events)} events")
        """
        # Parse query parameters (simplified - for Export API)
        # In production, this would parse YYYYMMDDTHH format
        if not query:
            raise QuerySyntaxError(
                "Query cannot be empty. Expected format: 'start=YYYYMMDDTHH&end=YYYYMMDDTHH'",
                details={"query": query},
            )

        try:
            # Make request to Export API
            url = f"{self.base_url}/api/2/export"
            response = self._api_call(url, method="GET", params={"q": query})
            return response if isinstance(response, list) else [response]
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                raise QuerySyntaxError(
                    f"Export query error: {e.response.text[:200]}",
                    details={"query": query, "status_code": 400},
                )
            raise ConnectionError(f"Failed to read data: {e}")

    # ========================================================================
    # Write Operations (Batch Event Upload)
    # ========================================================================

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record (single event).

        For bulk operations, use create_batch() instead.

        Args:
            object_name: "events" or "users"
            data: Event or user data as dictionary

        Returns:
            Response from API with ingestion status

        Raises:
            ValidationError: If data is invalid
            RateLimitError: If rate limit exceeded

        Example:
            >>> event = client.create("events", {
            ...     "user_id": "user123",
            ...     "event_type": "signup",
            ...     "time": int(time.time() * 1000)
            ... })
        """
        if object_name != "events":
            raise ObjectNotFoundError(
                f"Write operations only supported for 'events', got '{object_name}'",
                details={"object": object_name, "supported": ["events"]},
            )

        # Validate required fields
        if "user_id" not in data and "device_id" not in data:
            raise ValidationError(
                "Event must have either 'user_id' or 'device_id' (min 5 characters)",
                details={
                    "object": "events",
                    "missing_fields": ["user_id", "device_id"],
                    "note": "At least one is required, must be >= 5 characters",
                },
            )

        if "event_type" not in data:
            raise ValidationError(
                "Event must have 'event_type' field",
                details={
                    "object": "events",
                    "missing_fields": ["event_type"],
                },
            )

        # Upload as batch of 1
        return self.create_batch([data])

    def create_batch(
        self, events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Upload multiple events in batch.

        Args:
            events: List of event dictionaries (max 2000 events, max 20MB payload)

        Returns:
            Response with ingestion statistics:
            {
                "code": 200,
                "events_ingested": 50,
                "payload_size_bytes": 1024,
                "server_upload_time": 1234567890123
            }

        Raises:
            ValidationError: If batch is invalid
            RateLimitError: If batch exceeds rate limits
            ConnectionError: If API is unreachable

        Example:
            >>> events = [
            ...     {"user_id": "u1", "event_type": "page_view"},
            ...     {"user_id": "u2", "event_type": "click"},
            ... ]
            >>> result = client.create_batch(events)
            >>> print(f"Ingested {result['events_ingested']} events")
        """
        # Validate batch size
        if len(events) > 2000:
            raise ValidationError(
                f"Batch size cannot exceed 2000 events (got {len(events)})",
                details={
                    "provided": len(events),
                    "maximum": 2000,
                    "suggestion": "Split into smaller batches",
                },
            )

        if not events:
            raise ValidationError(
                "Batch cannot be empty",
                details={"provided": len(events), "minimum": 1},
            )

        # Build request
        payload = {
            "api_key": self.api_key,
            "events": events,
        }

        try:
            # Make request with proper headers
            url = f"{self.base_url}/batch"
            response = self.session.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()

            result = response.json()

            # Check for errors in response
            if result.get("code") != 200:
                if result.get("code") == 429:
                    raise RateLimitError(
                        f"Rate limit exceeded: {result.get('error', 'Unknown error')}",
                        details={
                            "code": 429,
                            "throttled_devices": result.get(
                                "throttled_devices", {}
                            ),
                            "throttled_users": result.get("throttled_users", {}),
                        },
                    )
                raise ValidationError(
                    f"Batch upload failed: {result.get('error', 'Unknown error')}",
                    details=result,
                )

            return result

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Batch upload timed out after {self.timeout} seconds",
                details={"timeout": self.timeout},
            )
        except requests.HTTPError as e:
            self._handle_api_error(e.response, "batch event upload")

    def update(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user properties via Identify API.

        Args:
            object_name: "users" (only supported object type)
            record_id: User ID to update
            data: User properties to update

        Returns:
            Identify API response

        Raises:
            ObjectNotFoundError: If object type not supported
            ValidationError: If data is invalid

        Example:
            >>> result = client.update("users", "user123", {
            ...     "user_properties": {
            ...         "plan": "premium",
            ...         "age": 30
            ...     }
            ... })
        """
        if object_name != "users":
            raise ObjectNotFoundError(
                f"Update operations only supported for 'users', got '{object_name}'",
                details={"object": object_name, "supported": ["users"]},
            )

        # Build identification object
        identification = {
            "user_id": record_id,
            **data,
        }

        try:
            url = f"{self.base_url}/identify"
            params = {
                "api_key": self.api_key,
                "identification": identification,
            }

            # Use form-urlencoded for Identify API
            response = self.session.post(
                url,
                data=params,
                timeout=self.timeout,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()

            return response.json()

        except requests.HTTPError as e:
            self._handle_api_error(e.response, "user identify")

    # ========================================================================
    # Session Management
    # ========================================================================

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication.

        Bug Prevention Pattern #1 & #2:
        - Use EXACT header names from API docs
        - Do NOT set Content-Type in session headers

        Returns:
            Configured requests.Session with auth headers
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
            }
        )
        # NOTE: Do NOT set Content-Type here!
        # Amplitude requires different Content-Type for different endpoints

        # Add authentication (use IF, not ELIF - multiple can coexist)
        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"

        if self.api_key:
            # API key is passed in request body or params, not headers
            # But we store it for later use in _api_call
            pass

        # Configure retries for resilience
        if self.max_retries > 0:
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

    def _api_call(
        self,
        endpoint: str,
        method: str = "GET",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make API call with automatic retry on rate limits.

        Args:
            endpoint: Full URL or path
            method: HTTP method (GET, POST, etc.)
            **kwargs: Additional request parameters

        Returns:
            Response data as dictionary

        Raises:
            RateLimitError: If rate limit exceeded after retries
            ConnectionError: If API is unreachable
        """
        for attempt in range(self.max_retries):
            try:
                if self.debug:
                    self.logger.debug(f"[DEBUG] {method} {endpoint}")

                response = self.session.request(
                    method, endpoint, timeout=self.timeout, **kwargs
                )
                response.raise_for_status()

                return self._parse_response(response)

            except requests.HTTPError as e:
                if e.response.status_code == 429:
                    # Rate limited - retry with exponential backoff
                    retry_after = int(
                        e.response.headers.get("Retry-After", 2 ** attempt)
                    )

                    if attempt < self.max_retries - 1:
                        if self.debug:
                            self.logger.debug(
                                f"[DEBUG] Rate limited. Retrying in {retry_after}s "
                                f"(attempt {attempt + 1}/{self.max_retries})"
                            )
                        time.sleep(retry_after)
                        continue
                    else:
                        raise RateLimitError(
                            f"API rate limit exceeded after {self.max_retries} attempts. "
                            f"Retry after {retry_after} seconds.",
                            details={
                                "retry_after": retry_after,
                                "attempts": self.max_retries,
                                "endpoint": endpoint,
                            },
                        )
                raise

    def _parse_response(
        self, response: requests.Response
    ) -> Dict[str, Any]:
        """
        Parse API response and extract data.

        Bug Prevention Pattern #3:
        - Try all known field name variations (case-sensitive!)
        - Handle both direct arrays and wrapped objects

        Args:
            response: HTTP response from API

        Returns:
            Response data as dictionary or list

        Raises:
            ConnectionError: If response is not valid JSON
        """
        try:
            data = response.json()
        except ValueError as e:
            raise ConnectionError(
                "Invalid JSON response from API",
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
            # Try all known field names (case-sensitive!)
            # Order: Try documented primary fields first, then common variations
            records = (
                data.get("root")
                or data.get("userData")
                or data.get("code")
                or data.get("events_ingested")
                or data.get("items")
                or data.get("data")
                or data.get("results")
                or data.get("Records")
                or data.get("records")
                or data
            )

            # Ensure we return appropriate type
            if isinstance(records, list):
                return records
            elif records is not None:
                return records if isinstance(records, dict) else [records]
            else:
                return data

        return {}

    def _handle_api_error(
        self, response: requests.Response, context: str = ""
    ):
        """
        Convert HTTP errors to structured driver exceptions.

        Args:
            response: Failed HTTP response
            context: Context string (e.g., "batch event upload")

        Raises:
            Appropriate DriverError subclass
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            error_msg = error_data.get("error", error_data.get("message", "Unknown error"))
        except ValueError:
            error_msg = response.text[:500]

        # Map status codes to exceptions
        if status_code == 401:
            raise AuthenticationError(
                f"Authentication failed: {error_msg}",
                details={
                    "status_code": 401,
                    "context": context,
                    "suggestion": "Check your API key",
                    "api_response": error_msg,
                },
            )

        elif status_code == 403:
            raise AuthenticationError(
                f"Permission denied: {error_msg}",
                details={
                    "status_code": 403,
                    "context": context,
                    "suggestion": "Verify your API key has required permissions",
                    "api_response": error_msg,
                },
            )

        elif status_code == 404:
            raise ObjectNotFoundError(
                f"Resource not found: {error_msg}",
                details={
                    "status_code": 404,
                    "context": context,
                    "api_response": error_msg,
                },
            )

        elif status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise RateLimitError(
                f"Rate limit exceeded: {error_msg}",
                details={
                    "status_code": 429,
                    "retry_after": retry_after,
                    "context": context,
                    "api_response": error_msg,
                },
            )

        elif status_code == 413:
            raise ValidationError(
                "Payload too large (exceeds 20MB limit)",
                details={
                    "status_code": 413,
                    "context": context,
                    "suggestion": "Split batch into smaller chunks",
                },
            )

        elif status_code >= 500:
            raise ConnectionError(
                f"API server error: {error_msg}",
                details={
                    "status_code": status_code,
                    "context": context,
                    "suggestion": "API server issue - try again later",
                    "api_response": error_msg,
                },
            )

        else:
            raise DriverError(
                f"API request failed: {error_msg}",
                details={
                    "status_code": status_code,
                    "context": context,
                    "api_response": error_msg,
                },
            )

    def _validate_connection(self):
        """
        Validate connection at init time (fail fast!).

        Makes a simple request to verify API key and connectivity.

        Raises:
            AuthenticationError: Invalid credentials
            ConnectionError: Cannot reach API
        """
        if not self.api_key:
            raise AuthenticationError(
                "API key is required but not set",
                details={
                    "suggestion": "Pass api_key to __init__ or use from_env()",
                    "env_var": "AMPLITUDE_API_KEY",
                },
            )

        # Try a simple list operation to validate connection
        try:
            # Create a minimal batch to test connectivity
            response = self.session.post(
                f"{self.base_url}/batch",
                json={"api_key": self.api_key, "events": []},
                timeout=self.timeout,
            )

            # 400 for empty events is expected - means API is reachable
            if response.status_code == 400:
                return

            # 401/403 means auth failed
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    "Invalid Amplitude API key or insufficient permissions",
                    details={
                        "status_code": response.status_code,
                        "api_response": response.text[:200],
                    },
                )

            # 2xx means success
            if 200 <= response.status_code < 300:
                return

            # Other errors
            raise ConnectionError(
                f"Cannot connect to Amplitude API (HTTP {response.status_code})",
                details={
                    "status_code": response.status_code,
                    "api_url": self.base_url,
                },
            )

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot reach Amplitude API at {self.base_url}",
                details={
                    "api_url": self.base_url,
                    "error": str(e),
                },
            )
        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"Connection to Amplitude API timed out",
                details={
                    "timeout": self.timeout,
                    "api_url": self.base_url,
                },
            )

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        Note: Amplitude doesn't provide rate limit headers in responses,
        so this returns a placeholder.

        Returns:
            Dictionary with rate limit information (if available)
        """
        return {
            "remaining": None,
            "limit": None,
            "reset_at": None,
            "retry_after": None,
            "note": "Amplitude does not expose rate limit headers",
        }

    def close(self):
        """
        Close session and cleanup resources.

        Example:
            >>> driver = AmplitudeDriver.from_env()
            >>> try:
            ...     result = driver.create_batch(events)
            ... finally:
            ...     driver.close()
        """
        if self.session:
            self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
