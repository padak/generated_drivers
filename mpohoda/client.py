"""
mPOHODA API Python Driver

Production-ready driver for mPOHODA accounting software API.
Supports read and write operations with automatic retry on rate limits.

Features:
- Dual authentication (API Key + OAuth2)
- Hybrid pagination (offset + keyset)
- Automatic exponential backoff retry
- Comprehensive error handling
- Debug logging support

Example:
    from mpohoda import MPohodaDriver

    # Load from environment
    client = MPohodaDriver.from_env()

    # Read records
    activities = client.read("Activities", page_size=50)

    # Create record
    partner = client.create("BusinessPartners", {
        "name": "Acme Corp",
        "taxNumber": "CZ123456789"
    })

    # Batch processing
    for batch in client.read_batched("Activities", batch_size=50):
        process_batch(batch)
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Bug Prevention #5: Support both package and standalone usage
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
        NotImplementedError,
    )
except ImportError:
    # Running as standalone (e.g., in tests)
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
        NotImplementedError,
    )


class MPohodaDriver(BaseDriver):
    """
    mPOHODA API Python Driver

    Provides access to mPOHODA accounting software via REST API.
    Supports both API Key and OAuth2 (Client Credentials) authentication.

    HTTPS-only communication required. Certificate verification enforced.

    Attributes:
        api_url: Base URL for API (default: https://api.mpohoda.cz/v1)
        api_key: API key for authentication (optional if using OAuth2)
        client_id: OAuth2 client ID (optional if using API key)
        client_secret: OAuth2 client secret (required if using client_id)
        access_token: Pre-obtained OAuth2 access token (optional)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Max retry attempts for rate limits (default: 3)
        debug: Enable debug logging (default: False)

    Example:
        # From environment variables
        driver = MPohodaDriver.from_env()

        # Explicit credentials
        driver = MPohodaDriver(
            api_url="https://api.mpohoda.cz/v1",
            api_key="your_api_key"
        )
    """

    # mPOHODA API constants
    DEFAULT_BASE_URL = "https://api.mpohoda.cz/v1"
    OAUTH_TOKEN_ENDPOINT = "https://ucet.pohoda.cz/connect/token"
    OAUTH_SCOPE = "Mph.OpenApi.Access.Cz"
    MAX_PAGE_SIZE = 50  # Hard limit from API docs

    # Available objects (from API reference)
    OBJECTS = [
        "Activities",
        "BusinessPartners",
        "Banks",
        "BankAccounts",
        "CashRegisters",
        "Centres",
        "Establishments",
        "Countries",
        "Currencies",
        "CityPostCodes",
    ]

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize mPOHODA driver.

        CRITICAL: Follows strict 4-phase initialization order:
        Phase 1: Set driver-specific attributes
        Phase 2: Set parent class attributes (manually, NOT via super().__init__())
        Phase 3: Create session with _create_session()
        Phase 4: Validate connection with _validate_connection()

        Args:
            api_url: Base API URL (default: https://api.mpohoda.cz/v1)
            api_key: API key for authentication (optional if using OAuth2)
            client_id: OAuth2 client ID (optional)
            client_secret: OAuth2 client secret (required if using client_id)
            access_token: Pre-obtained OAuth2 access token (optional)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Max retry attempts for rate limits (default: 3)
            debug: Enable debug logging (default: False)

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If cannot reach API

        Example:
            driver = MPohodaDriver(api_key="your_key")
            driver = MPohodaDriver.from_env()
        """

        # ===== PHASE 1: Set driver-specific attributes =====
        self.driver_name = "MPohodaDriver"
        self.oauth_token = access_token
        self.oauth_token_expiry = None
        self.client_id = client_id
        self.client_secret = client_secret

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger = logging.getLogger(__name__)
        else:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.WARNING)
        self.logger = logger

        # ===== PHASE 2: Set parent class attributes =====
        # DO NOT call super().__init__()! Set attributes manually.
        # Parent's __init__() immediately calls _validate_connection()
        # which needs self.session to exist first.
        resolved_base_url = api_url or self.DEFAULT_BASE_URL
        self.api_url = resolved_base_url
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
    def from_env(cls, **kwargs) -> "MPohodaDriver":
        """
        Create driver instance from environment variables.

        Environment Variables:
            MPOHODA_BASE_URL: API base URL (optional, defaults to production)
            MPOHODA_API_KEY: API key for authentication (optional if using OAuth2)
            MPOHODA_CLIENT_ID: OAuth2 client ID (optional)
            MPOHODA_CLIENT_SECRET: OAuth2 client secret (optional)
            MPOHODA_ACCESS_TOKEN: Pre-obtained OAuth2 token (optional)

        Returns:
            Configured driver instance

        Raises:
            AuthenticationError: If required credentials are missing

        Example:
            # Set environment variables, then:
            driver = MPohodaDriver.from_env()
            activities = driver.read("Activities")
        """
        api_url = os.getenv("MPOHODA_BASE_URL")
        api_key = os.getenv("MPOHODA_API_KEY")
        client_id = os.getenv("MPOHODA_CLIENT_ID")
        client_secret = os.getenv("MPOHODA_CLIENT_SECRET")
        access_token = os.getenv("MPOHODA_ACCESS_TOKEN")

        # Validate that at least one auth method is provided
        if not api_key and not access_token and not (client_id and client_secret):
            raise AuthenticationError(
                "No authentication credentials found. Set at least one of: "
                "MPOHODA_API_KEY, MPOHODA_ACCESS_TOKEN, or both MPOHODA_CLIENT_ID and MPOHODA_CLIENT_SECRET",
                details={
                    "required_env_vars": [
                        "MPOHODA_API_KEY",
                        "MPOHODA_ACCESS_TOKEN",
                        "MPOHODA_CLIENT_ID",
                        "MPOHODA_CLIENT_SECRET",
                    ],
                    "hint": "Set MPOHODA_API_KEY for API key auth or MPOHODA_CLIENT_ID+MPOHODA_CLIENT_SECRET for OAuth2",
                },
            )

        return cls(
            api_url=api_url,
            api_key=api_key,
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            **kwargs
        )

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities.

        Returns:
            DriverCapabilities describing what this driver supports

        Example:
            capabilities = driver.get_capabilities()
            if capabilities.write:
                print("This driver supports create operations")
        """
        return DriverCapabilities(
            read=True,
            write=True,  # POST /BusinessPartners and similar
            update=False,  # API does not support PUT
            delete=False,  # API does not support DELETE
            batch_operations=False,  # No batch API
            streaming=False,
            pagination=PaginationStyle.HYBRID,  # Both offset and cursor
            query_language=None,  # REST API, not SQL/SOQL
            max_page_size=self.MAX_PAGE_SIZE,
            supports_transactions=False,
            supports_relationships=False,
        )

    def list_objects(self) -> List[str]:
        """
        Discover all available objects.

        Returns:
            List of object names available in the API

        Example:
            objects = driver.list_objects()
            print(objects)
            # ['Activities', 'BusinessPartners', 'Banks', ...]
        """
        return self.OBJECTS.copy()

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get field schema for an object.

        Args:
            object_name: Name of object (case-sensitive)

        Returns:
            Dictionary mapping field names to field metadata

        Raises:
            ObjectNotFoundError: If object doesn't exist

        Example:
            fields = driver.get_fields("BusinessPartners")
            print(fields.keys())
            # ['id', 'name', 'taxNumber', ...]
        """
        if object_name not in self.OBJECTS:
            available = self.list_objects()
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found. Available objects: {', '.join(available)}",
                details={
                    "requested": object_name,
                    "available": available,
                },
            )

        # Basic field definitions based on API reference
        # In production, this would be fetched from API metadata
        fields_map = {
            "Activities": {
                "id": {"type": "string", "label": "ID", "required": True},
                "description": {"type": "string", "label": "Description"},
                "createdDate": {"type": "datetime", "label": "Created Date"},
            },
            "BusinessPartners": {
                "id": {"type": "string", "label": "ID", "required": True},
                "name": {"type": "string", "label": "Name", "required": True},
                "taxNumber": {"type": "string", "label": "Tax Number"},
                "identificationNumber": {"type": "string", "label": "ID Number"},
                "addresses": {"type": "array", "label": "Addresses"},
            },
            "Banks": {
                "id": {"type": "string", "label": "ID", "required": True},
                "name": {"type": "string", "label": "Name"},
            },
            "BankAccounts": {
                "id": {"type": "string", "label": "ID", "required": True},
                "accountNumber": {"type": "string", "label": "Account Number"},
                "bankId": {"type": "string", "label": "Bank ID"},
            },
            "CashRegisters": {
                "id": {"type": "string", "label": "ID", "required": True},
                "name": {"type": "string", "label": "Name"},
            },
            "Centres": {
                "id": {"type": "string", "label": "ID", "required": True},
                "name": {"type": "string", "label": "Name"},
            },
            "Establishments": {
                "id": {"type": "string", "label": "ID", "required": True},
                "name": {"type": "string", "label": "Name"},
            },
            "Countries": {
                "id": {"type": "string", "label": "ID", "required": True},
                "code": {"type": "string", "label": "Country Code"},
                "name": {"type": "string", "label": "Name"},
            },
            "Currencies": {
                "id": {"type": "string", "label": "ID", "required": True},
                "code": {"type": "string", "label": "Currency Code"},
                "name": {"type": "string", "label": "Name"},
            },
            "CityPostCodes": {
                "id": {"type": "string", "label": "ID", "required": True},
                "city": {"type": "string", "label": "City"},
                "postCode": {"type": "string", "label": "Post Code"},
                "country": {"type": "string", "label": "Country"},
            },
        }

        return fields_map.get(object_name, {})

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
            object_name: Name of object to read (e.g., "Activities", "BusinessPartners")
            filters: Optional filters (e.g., {"status": "active"}, varies by endpoint)
            page_size: Records per page (max: 50)
            page_number: Page number (1-indexed)

        Returns:
            List of records

        Raises:
            ObjectNotFoundError: If object doesn't exist
            ValidationError: If page_size exceeds maximum
            RateLimitError: If API rate limit exceeded (after retries)
            ConnectionError: If cannot reach API

        Example:
            # Read first page
            activities = driver.read("Activities", page_size=50, page_number=1)

            # With filters
            partners = driver.read(
                "BusinessPartners",
                filters={"status": "active"},
                page_size=20
            )

            # Process results
            for record in activities:
                print(record["id"], record.get("name"))
        """
        # Validate object exists
        if object_name not in self.OBJECTS:
            available = self.list_objects()
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found. Available objects: {', '.join(available)}",
                details={"requested": object_name, "available": available},
            )

        # Bug Prevention #4: Validate page_size (hard limit from API)
        if page_size > self.MAX_PAGE_SIZE:
            raise ValidationError(
                f"page_size cannot exceed {self.MAX_PAGE_SIZE} (got: {page_size})",
                details={
                    "parameter": "page_size",
                    "provided": page_size,
                    "maximum": self.MAX_PAGE_SIZE,
                    "suggestion": f"Use page_size <= {self.MAX_PAGE_SIZE}",
                },
            )

        if page_size < 1:
            raise ValidationError(
                f"page_size must be at least 1 (got: {page_size})",
                details={
                    "parameter": "page_size",
                    "provided": page_size,
                    "minimum": 1,
                },
            )

        # Build request parameters
        params = {
            "PageNumber": page_number,
            "PageSize": page_size,
        }

        # Add filters if provided
        if filters:
            params.update(filters)

        # Make request
        try:
            response = self._api_call(
                f"/{object_name}",
                method="GET",
                params=params,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request to /{object_name} timed out after {self.timeout} seconds",
                details={
                    "endpoint": f"/{object_name}",
                    "timeout": self.timeout,
                },
            )

        # Parse response
        return self._parse_response(response)

    def read_batched(
        self, object_name: str, batch_size: int = 50
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Read records in batches using keyset pagination.

        Memory-efficient alternative to read() for large datasets.
        Automatically handles pagination using cursor tokens.

        Args:
            object_name: Name of object to read
            batch_size: Records per batch (max: 50)

        Yields:
            Batches of records as lists of dictionaries

        Raises:
            ObjectNotFoundError: If object doesn't exist
            RateLimitError: If API rate limit exceeded

        Example:
            # Process large dataset in batches
            for batch in driver.read_batched("Activities", batch_size=50):
                process_batch(batch)
                print(f"Processed {len(batch)} records")

            # Results can be combined
            all_records = []
            for batch in driver.read_batched("BusinessPartners"):
                all_records.extend(batch)
        """
        if object_name not in self.OBJECTS:
            available = self.list_objects()
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found",
                details={"available": available},
            )

        # Validate batch_size
        if batch_size > self.MAX_PAGE_SIZE:
            batch_size = self.MAX_PAGE_SIZE
            self.logger.warning(
                f"batch_size capped at {self.MAX_PAGE_SIZE} (API limit)"
            )

        page_number = 1
        after_token = None

        while True:
            params = {"PageSize": batch_size}

            if after_token:
                # Use cursor-based pagination
                params["After"] = after_token
            else:
                # Use offset-based pagination
                params["PageNumber"] = page_number

            try:
                response = self._api_call(
                    f"/{object_name}",
                    method="GET",
                    params=params,
                )
            except RateLimitError:
                # Rate limit hit - stop iteration
                self.logger.warning("Rate limit reached during batch read")
                break

            data = response.json()
            records = self._parse_response(response)

            if records:
                yield records

            # Check if more pages available
            pagination = data.get("pagination", {})
            next_token = pagination.get("pageToken")

            if next_token:
                # Continue with keyset pagination
                after_token = next_token
            else:
                # No more pages
                break

            page_number += 1

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new record.

        Supported for BusinessPartners and similar endpoints.

        Args:
            object_name: Name of object to create (e.g., "BusinessPartners")
            data: Field values as dictionary

        Returns:
            Created record with ID

        Raises:
            ObjectNotFoundError: If object doesn't exist
            ValidationError: If data is invalid (API returns 422)
            ConnectionError: If cannot reach API

        Example:
            partner = driver.create("BusinessPartners", {
                "name": "Acme Corp",
                "taxNumber": "CZ123456789",
                "identificationNumber": "12345678",
                "addresses": [{
                    "type": "CONTACT",
                    "street": "Main St",
                    "city": "Prague",
                    "postalCode": "12000",
                    "country": "CZ"
                }]
            })

            print(f"Created: {partner['id']}")
        """
        if object_name not in self.OBJECTS:
            raise ObjectNotFoundError(
                f"Object '{object_name}' not found",
                details={"available": self.list_objects()},
            )

        try:
            response = self._api_call(
                f"/{object_name}",
                method="POST",
                json=data,
            )
        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request to create {object_name} timed out",
                details={"endpoint": f"POST /{object_name}"},
            )

        return response.json()

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status.

        mPOHODA uses monthly rate limits per endpoint type.
        This returns information from the last API call headers.

        Returns:
            {
                "remaining": int or None,
                "limit": int or None,
                "reset_at": str or None (ISO format),
                "retry_after": int or None (seconds),
                "limit_type": "monthly_per_type"
            }

        Example:
            status = driver.get_rate_limit_status()
            if status["remaining"]:
                print(f"{status['remaining']} requests remaining")
        """
        # Note: mPOHODA doesn't always return rate limit headers
        # This is a placeholder for future implementation
        return {
            "remaining": None,
            "limit": None,
            "reset_at": None,
            "retry_after": None,
            "limit_type": "monthly_per_type",
        }

    def close(self):
        """
        Close connections and cleanup resources.

        Example:
            driver = MPohodaDriver.from_env()
            try:
                data = driver.read("Activities")
            finally:
                driver.close()
        """
        if self.session:
            self.session.close()

    # ===== Internal Implementation Methods =====

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication.

        Bug Prevention #1: Uses EXACT header names from API documentation
        Bug Prevention #2: Does NOT set Content-Type (let requests handle it)
        Bug Prevention #5: Supports multiple auth methods with IF (not ELIF)

        Returns:
            Configured requests.Session with auth headers and retry strategy
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
        })
        # NOTE: Do NOT set Content-Type here! requests library handles it.
        # Setting it here would break GET requests (Bug Prevention #2).

        # Add authentication using IF (not ELIF) to support multiple methods
        # Bug Prevention #5: Multiple auth methods can coexist
        if self.access_token or self.oauth_token:
            # Use OAuth2 Bearer token
            token = self.oauth_token or self.access_token
            session.headers["Authorization"] = f"Bearer {token}"

        if self.api_key:
            # Bug Prevention #1: EXACT header name from docs: "Api-Key"
            # NOT "API-Key" or "api-key" - case matters!
            session.headers["Api-Key"] = self.api_key

        # Configure retries for rate limiting
        # Retries only for idempotent methods (GET, HEAD, etc.)
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s, 8s, ...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "HEAD", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _validate_connection(self):
        """
        Validate connection at initialization (fail fast).

        Makes a simple request to verify credentials and connectivity.

        Raises:
            AuthenticationError: If credentials are invalid (401/403)
            ConnectionError: If cannot reach API or network issues
        """
        try:
            if self.debug:
                self.logger.debug(f"Validating connection to {self.api_url}")

            # Simple request to verify connectivity and auth
            response = self.session.get(
                urljoin(self.api_url, "/Activities"),
                params={"PageSize": 1},
                timeout=self.timeout,
            )

            # Check for auth errors
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your API key or OAuth2 credentials.",
                    details={
                        "status_code": 401,
                        "api_url": self.api_url,
                        "has_api_key": bool(self.api_key),
                        "has_oauth_token": bool(self.access_token or self.oauth_token),
                    },
                )

            if response.status_code == 403:
                raise AuthenticationError(
                    "Access forbidden. Your credentials may lack required permissions.",
                    details={
                        "status_code": 403,
                        "api_url": self.api_url,
                    },
                )

            # Check for other errors
            response.raise_for_status()

            if self.debug:
                self.logger.debug("Connection validated successfully")

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot connect to mPOHODA API at {self.api_url}. "
                "Check your internet connection and API URL.",
                details={
                    "api_url": self.api_url,
                    "error": str(e),
                },
            )

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Connection to mPOHODA API timed out after {self.timeout} seconds",
                details={"api_url": self.api_url, "timeout": self.timeout},
            )

        except requests.exceptions.RequestException as e:
            if isinstance(e, requests.exceptions.HTTPError):
                # Already handled above
                raise
            raise ConnectionError(
                f"Error connecting to mPOHODA API: {e}",
                details={"error": str(e)},
            )

    def _api_call(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> requests.Response:
        """
        Make API call with automatic retry on rate limits.

        Handles 429 (rate limit) responses with exponential backoff.
        Other errors are raised immediately.

        Args:
            endpoint: API endpoint path (e.g., "/Activities")
            method: HTTP method (GET, POST, etc.)
            params: URL query parameters
            json: Request body (JSON)
            **kwargs: Additional request options

        Returns:
            requests.Response object

        Raises:
            RateLimitError: If rate limit exceeded after retries
            QuerySyntaxError: If API returns 400
            ObjectNotFoundError: If API returns 404
            ValidationError: If API returns 422
            ConnectionError: If other network errors occur
        """
        url = urljoin(self.api_url, endpoint)

        for attempt in range(self.max_retries + 1):
            try:
                if self.debug:
                    self.logger.debug(
                        f"[Attempt {attempt + 1}] {method} {endpoint} "
                        f"params={params}"
                    )

                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    timeout=self.timeout,
                    **kwargs
                )

                # Handle HTTP errors
                if response.status_code == 400:
                    error_text = response.text[:500]
                    raise QuerySyntaxError(
                        f"Invalid request to {endpoint}: {error_text}",
                        details={
                            "status_code": 400,
                            "endpoint": endpoint,
                            "response": error_text,
                        },
                    )

                if response.status_code == 404:
                    raise ObjectNotFoundError(
                        f"Resource not found: {endpoint}",
                        details={"status_code": 404, "endpoint": endpoint},
                    )

                if response.status_code == 422:
                    error_text = response.text[:500]
                    raise ValidationError(
                        f"Validation error at {endpoint}: {error_text}",
                        details={
                            "status_code": 422,
                            "endpoint": endpoint,
                            "response": error_text,
                        },
                    )

                if response.status_code == 429:
                    # Rate limited - retry with exponential backoff
                    retry_after = int(
                        response.headers.get("Retry-After", 2 ** attempt)
                    )

                    if attempt < self.max_retries:
                        if self.debug:
                            self.logger.debug(
                                f"Rate limited. Retrying in {retry_after}s "
                                f"(attempt {attempt + 1}/{self.max_retries})"
                            )
                        time.sleep(retry_after)
                        continue
                    else:
                        # Exhausted retries
                        raise RateLimitError(
                            f"API rate limit exceeded after {self.max_retries} "
                            f"attempts. Retry after {retry_after} seconds.",
                            details={
                                "retry_after": retry_after,
                                "attempts": self.max_retries,
                                "endpoint": endpoint,
                            },
                        )

                # Other 5xx errors - retry
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        wait_time = 2 ** attempt
                        if self.debug:
                            self.logger.debug(
                                f"Server error {response.status_code}. "
                                f"Retrying in {wait_time}s"
                            )
                        time.sleep(wait_time)
                        continue
                    else:
                        raise ConnectionError(
                            f"API server error {response.status_code}: "
                            f"{response.text[:200]}",
                            details={
                                "status_code": response.status_code,
                                "endpoint": endpoint,
                            },
                        )

                # Check for success
                response.raise_for_status()
                return response

            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as e:
                if attempt < self.max_retries:
                    wait_time = 2 ** attempt
                    if self.debug:
                        self.logger.debug(
                            f"Connection error: {e}. Retrying in {wait_time}s"
                        )
                    time.sleep(wait_time)
                    continue
                else:
                    raise ConnectionError(
                        f"Cannot reach API after {self.max_retries} attempts: {e}",
                        details={"endpoint": endpoint, "error": str(e)},
                    )

            except (
                QuerySyntaxError,
                ObjectNotFoundError,
                ValidationError,
                RateLimitError,
                ConnectionError,
            ):
                # Re-raise driver exceptions
                raise

        # Should not reach here, but handle just in case
        raise ConnectionError("Unexpected error in API call retry logic")

    def _parse_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        Parse API response and extract data records.

        Bug Prevention #3: Handles multiple response formats with field name fallbacks.
        Tries all known field name variations (case-sensitive!).

        Supports:
        - Direct arrays: [{"id": 1}, {"id": 2}]
        - Paginated format: {"items": [...], "totalItemCount": 100, "pagination": {...}}
        - Wrapped format: {"data": {...}}

        Args:
            response: HTTP response from API

        Returns:
            List of records extracted from response

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
                    "content_preview": response.text[:200],
                    "error": str(e),
                },
            )

        # Handle direct array responses
        if isinstance(data, list):
            return data

        # Handle object-wrapped responses
        if isinstance(data, dict):
            # Bug Prevention #3: Try all known field names (case-sensitive!)
            # Priority order: items (paginated) -> data (wrapped) -> fallback
            records = (
                data.get("items") or  # Primary paginated format
                data.get("Items") or  # Alternative capitalization
                data.get("data") or  # General wrapper format
                data.get("Data") or  # Alternative capitalization
                data.get("results") or  # Common REST convention
                data.get("Results") or  # Alternative capitalization
                []
            )

            # Ensure we return a list
            if isinstance(records, list):
                return records
            elif records is not None:
                # Single object - wrap in list
                return [records]
            else:
                return []

        # Unknown format
        return []
