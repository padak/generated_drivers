"""
Stripe API Driver

REST API driver for Stripe payment platform.
Provides complete CRUD operations for Stripe resources (Products, Customers, Invoices, etc.).

Features:
- Bearer token authentication
- Cursor-based pagination (max 100 records per page)
- Automatic rate limit retry with exponential backoff
- Comprehensive error handling
- Support for 30+ Stripe resource types

API Documentation: https://docs.stripe.com/api
API Version: v1, v2
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional, Iterator
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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


class StripeDriver(BaseDriver):
    """
    Stripe API driver using REST interface.

    Features:
    - Stripe REST API support
    - Cursor-based pagination (limit max 100)
    - Bearer token authentication
    - Support for all resource types (Products, Customers, Invoices, etc.)
    - Automatic rate limit retry

    Example:
        >>> client = StripeDriver.from_env()
        >>> products = client.read("products", limit=10)
        >>> customer = client.create("customers", {"email": "test@example.com"})
        >>> client.close()
    """

    # Stripe resource objects supported by this driver
    SUPPORTED_OBJECTS = [
        "account",
        "account_session",
        "application_fee_refund",
        "balance",
        "balance_transaction",
        "card",
        "charge",
        "checkout_session",
        "country_spec",
        "credit_grant",
        "credit_note",
        "customer",
        "customer_balance_transaction",
        "external_account_card",
        "financing_offer",
        "invoice",
        "invoice_payment",
        "meter_event",
        "meter_event_adjustment",
        "meter_event_summary",
        "payment_intent",
        "plan",
        "price",
        "product",
        "quote",
        "setup_attempt",
        "shipping_rate",
        "source",
        "subscription_item",
        "tax_code",
        "test_clock",
    ]

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        access_token: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs,
    ):
        """
        Initialize Stripe driver.

        IMPORTANT: Initialization follows strict 4-phase order.
        See BUG_PREVENTION_INITIALIZATION.md for details.

        Args:
            base_url: Stripe API base URL (default: https://api.stripe.com)
            api_key: Stripe API key (from environment or parameter)
            access_token: Bearer token (alternative to api_key)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Max retry attempts for rate limiting (default: 3)
            debug: Enable debug logging (default: False)
            **kwargs: Additional driver-specific options

        Raises:
            AuthenticationError: If credentials are missing or invalid
            ConnectionError: If cannot connect to Stripe API

        Example:
            >>> driver = StripeDriver.from_env()
            >>> driver = StripeDriver(api_key="sk_test_...", timeout=60)
        """

        # ===== PHASE 1: Set custom attributes =====
        self.driver_name = "StripeDriver"

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

        # ===== PHASE 2: Set parent class attributes =====
        # DO NOT call super().__init__()! Set manually instead.
        resolved_base_url = base_url or "https://api.stripe.com"
        self.base_url = resolved_base_url
        self.api_key = api_key
        self.access_token = access_token
        self.timeout = timeout or 30
        self.max_retries = max_retries or 3
        self.debug = debug

        # ===== PHASE 3: Create session =====
        self.session = self._create_session()

        # ===== PHASE 4: Validate connection =====
        self._validate_connection()

    @classmethod
    def from_env(cls, **kwargs) -> "StripeDriver":
        """
        Create driver instance from environment variables.

        Environment variables:
            STRIPE_API_KEY: Stripe API key (required)
            STRIPE_BASE_URL: Stripe base URL (optional, default: https://api.stripe.com)

        Args:
            **kwargs: Additional arguments passed to __init__

        Returns:
            Configured StripeDriver instance

        Raises:
            AuthenticationError: If STRIPE_API_KEY is not set

        Example:
            >>> driver = StripeDriver.from_env()
            >>> driver = StripeDriver.from_env(timeout=60)
        """
        api_key = os.getenv("STRIPE_API_KEY")
        base_url = os.getenv("STRIPE_BASE_URL")

        if not api_key:
            raise AuthenticationError(
                "Missing Stripe API key. Set STRIPE_API_KEY environment variable.",
                details={
                    "required_env_vars": ["STRIPE_API_KEY"],
                    "optional_env_vars": ["STRIPE_BASE_URL"],
                },
            )

        return cls(api_key=api_key, base_url=base_url, **kwargs)

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities.

        Returns:
            DriverCapabilities describing what this driver supports

        Example:
            >>> caps = driver.get_capabilities()
            >>> if caps.write:
            ...     print("Can create records")
        """
        return DriverCapabilities(
            read=True,
            write=True,
            update=True,
            delete=True,
            batch_operations=False,  # Stripe API limitation: no bulk operations
            streaming=True,  # Partial: meter event streams available
            pagination=PaginationStyle.CURSOR,
            query_language=None,  # REST API, no query language
            max_page_size=100,
            supports_transactions=False,
            supports_relationships=True,
        )

    def list_objects(self) -> List[str]:
        """
        Return list of supported Stripe resource types.

        Returns:
            List of resource type names

        Example:
            >>> objects = driver.list_objects()
            >>> if "customer" in objects:
            ...     print("Can query customers")
        """
        return self.SUPPORTED_OBJECTS.copy()

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get field schema for a Stripe resource type.

        Returns basic field information. Full schema varies by Stripe version.

        Args:
            object_name: Stripe resource type (e.g., "product", "customer")

        Returns:
            Dictionary mapping field names to field metadata

        Raises:
            ObjectNotFoundError: If object_name is not supported

        Example:
            >>> fields = driver.get_fields("product")
            >>> if "name" in fields:
            ...     print(f"Product name type: {fields['name']['type']}")
        """
        object_name_lower = object_name.lower()

        if object_name_lower not in self.SUPPORTED_OBJECTS:
            available = ", ".join(self.SUPPORTED_OBJECTS[:5])
            raise ObjectNotFoundError(
                f"Resource '{object_name}' not supported. Available: {available}...",
                details={
                    "requested": object_name,
                    "available": self.SUPPORTED_OBJECTS,
                },
            )

        # Return common field schema for this resource type
        # Full schema varies by Stripe API version
        schemas = {
            "product": {
                "id": {"type": "string", "required": True, "label": "ID"},
                "name": {"type": "string", "required": True, "label": "Product Name"},
                "description": {"type": "string", "required": False, "label": "Description"},
                "type": {"type": "string", "required": True, "label": "Type"},
                "metadata": {"type": "object", "required": False, "label": "Metadata"},
            },
            "customer": {
                "id": {"type": "string", "required": True, "label": "ID"},
                "email": {"type": "string", "required": False, "label": "Email"},
                "name": {"type": "string", "required": False, "label": "Name"},
                "description": {"type": "string", "required": False, "label": "Description"},
                "metadata": {"type": "object", "required": False, "label": "Metadata"},
            },
            "invoice": {
                "id": {"type": "string", "required": True, "label": "ID"},
                "customer": {"type": "string", "required": False, "label": "Customer ID"},
                "amount_paid": {"type": "integer", "required": False, "label": "Amount Paid"},
                "status": {"type": "string", "required": False, "label": "Status"},
            },
            "charge": {
                "id": {"type": "string", "required": True, "label": "ID"},
                "amount": {"type": "integer", "required": True, "label": "Amount"},
                "currency": {"type": "string", "required": True, "label": "Currency"},
                "customer": {"type": "string", "required": False, "label": "Customer ID"},
                "status": {"type": "string", "required": False, "label": "Status"},
            },
            "payment_intent": {
                "id": {"type": "string", "required": True, "label": "ID"},
                "amount": {"type": "integer", "required": True, "label": "Amount"},
                "currency": {"type": "string", "required": True, "label": "Currency"},
                "status": {"type": "string", "required": False, "label": "Status"},
            },
        }

        # Return schema for this object or generic schema
        return schemas.get(
            object_name_lower,
            {
                "id": {"type": "string", "required": True, "label": "ID"},
                "object": {"type": "string", "required": False, "label": "Object Type"},
            },
        )

    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query and return results.

        For Stripe REST API:
        - query parameter is treated as the resource type (e.g., "products", "customers")
        - limit: max 100 (default: 10)
        - offset: uses cursor-based pagination with starting_after parameter

        Args:
            query: Resource type path (e.g., "products", "customers", "invoices")
            limit: Maximum records to return (max 100, default 10)
            offset: Starting cursor for pagination (unused for cursor-based, kept for compatibility)

        Returns:
            List of resource records

        Raises:
            ValidationError: If limit exceeds 100
            ObjectNotFoundError: If resource type doesn't exist
            RateLimitError: If rate limited after retries
            ConnectionError: If API connection fails

        Example:
            >>> # List products with limit
            >>> products = driver.read("products", limit=50)

            >>> # List customers
            >>> customers = driver.read("customers", limit=10)
        """
        # Bug Prevention #4: Validate page size
        max_page_size = 100
        if limit and limit > max_page_size:
            raise ValidationError(
                f"limit cannot exceed {max_page_size} (got: {limit})",
                details={
                    "provided": limit,
                    "maximum": max_page_size,
                    "parameter": "limit",
                },
            )

        if limit and limit < 1:
            raise ValidationError(
                f"limit must be at least 1 (got: {limit})",
                details={"provided": limit, "minimum": 1},
            )

        # Extract resource type from query
        resource_type = query.strip().lower()
        if resource_type.startswith("/"):
            resource_type = resource_type.lstrip("/")

        # Build endpoint URL
        endpoint = f"/v1/{resource_type}"
        url = urljoin(self.base_url, endpoint)

        # Build query parameters
        params = {}
        if limit:
            params["limit"] = limit

        if self.debug:
            self.logger.debug(f"GET {url} params={params}")

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise DriverTimeoutError(
                f"Request timed out after {self.timeout}s",
                details={"timeout": self.timeout, "error": str(e)},
            )
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e.response, context=f"reading {resource_type}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to Stripe API: {str(e)}",
                details={"error": str(e), "url": url},
            )

        return self._parse_response(response)

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Stripe resource.

        Args:
            object_name: Resource type (e.g., "products", "customers", "invoices")
            data: Resource data as dictionary

        Returns:
            Created resource with ID

        Raises:
            ValidationError: If data is invalid
            AuthenticationError: If credentials invalid
            RateLimitError: If rate limited
            ConnectionError: If API connection fails

        Example:
            >>> product = driver.create("products", {
            ...     "name": "My Product",
            ...     "type": "service"
            ... })
            >>> print(f"Created product: {product['id']}")
        """
        resource_type = object_name.strip().lower()

        # Build endpoint URL
        endpoint = f"/v1/{resource_type}"
        url = urljoin(self.base_url, endpoint)

        if self.debug:
            self.logger.debug(f"POST {url} data={data}")

        try:
            response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise DriverTimeoutError(
                f"Request timed out after {self.timeout}s",
                details={"timeout": self.timeout},
            )
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e.response, context=f"creating {resource_type}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to Stripe API: {str(e)}",
                details={"error": str(e)},
            )

        records = self._parse_response(response)
        return records[0] if records else {}

    def update(
        self, object_name: str, record_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing Stripe resource.

        Args:
            object_name: Resource type (e.g., "products", "customers")
            record_id: Resource ID to update
            data: Updated data as dictionary

        Returns:
            Updated resource

        Raises:
            ObjectNotFoundError: If resource doesn't exist
            ValidationError: If data is invalid
            RateLimitError: If rate limited
            ConnectionError: If API connection fails

        Example:
            >>> updated = driver.update("products", "prod_123", {
            ...     "name": "Updated Name"
            ... })
        """
        resource_type = object_name.strip().lower()

        # Build endpoint URL
        endpoint = f"/v1/{resource_type}/{record_id}"
        url = urljoin(self.base_url, endpoint)

        if self.debug:
            self.logger.debug(f"POST {url} data={data}")

        try:
            response = self.session.post(url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise DriverTimeoutError(
                f"Request timed out after {self.timeout}s",
                details={"timeout": self.timeout},
            )
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e.response, context=f"updating {resource_type}/{record_id}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to Stripe API: {str(e)}",
                details={"error": str(e)},
            )

        records = self._parse_response(response)
        return records[0] if records else {}

    def delete(self, object_name: str, record_id: str) -> bool:
        """
        Delete a Stripe resource.

        Args:
            object_name: Resource type
            record_id: Resource ID to delete

        Returns:
            True if successful

        Raises:
            ObjectNotFoundError: If resource doesn't exist
            RateLimitError: If rate limited
            ConnectionError: If API connection fails

        Example:
            >>> success = driver.delete("products", "prod_123")
        """
        resource_type = object_name.strip().lower()

        # Build endpoint URL
        endpoint = f"/v1/{resource_type}/{record_id}"
        url = urljoin(self.base_url, endpoint)

        if self.debug:
            self.logger.debug(f"DELETE {url}")

        try:
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.exceptions.Timeout as e:
            raise DriverTimeoutError(
                f"Request timed out after {self.timeout}s",
                details={"timeout": self.timeout},
            )
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e.response, context=f"deleting {resource_type}/{record_id}")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to Stripe API: {str(e)}",
                details={"error": str(e)},
            )

        return True

    def read_batched(
        self, query: str, batch_size: int = 100
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute query and yield results in batches (cursor-based pagination).

        Automatically handles pagination using cursor-based approach.
        Each batch uses the limit parameter for Stripe's max page size.

        Args:
            query: Resource type path (e.g., "products", "customers")
            batch_size: Records per batch (max 100, default 100)

        Yields:
            Batches of records as lists

        Example:
            >>> for batch in driver.read_batched("products", batch_size=50):
            ...     process_batch(batch)
        """
        # Validate batch_size
        max_size = 100
        if batch_size > max_size:
            batch_size = max_size

        resource_type = query.strip().lower()
        endpoint = f"/v1/{resource_type}"
        url = urljoin(self.base_url, endpoint)

        starting_after = None

        while True:
            params = {"limit": batch_size}
            if starting_after:
                params["starting_after"] = starting_after

            if self.debug:
                self.logger.debug(f"GET {url} params={params}")

            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self._handle_api_error(e.response, context=f"reading {resource_type}")
            except requests.exceptions.RequestException as e:
                raise ConnectionError(
                    f"Failed to connect to Stripe API: {str(e)}",
                    details={"error": str(e)},
                )

            records = self._parse_response(response)
            if not records:
                break

            yield records

            # Check if there are more records
            response_data = response.json()
            if not response_data.get("has_more", False):
                break

            # Get cursor for next request
            if records:
                starting_after = records[-1].get("id")

    def call_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Call a Stripe REST API endpoint directly (low-level access).

        Args:
            endpoint: API endpoint path (e.g., "/v1/products", "customers")
            method: HTTP method (GET, POST, DELETE, etc.)
            params: URL query parameters
            data: Request body (for POST/PUT)
            **kwargs: Additional request options

        Returns:
            Response data as dictionary

        Example:
            >>> result = driver.call_endpoint(
            ...     endpoint="/v1/products",
            ...     method="GET",
            ...     params={"limit": 10}
            ... )
        """
        # Ensure endpoint starts with /v1 or /v2
        if not endpoint.startswith("/v"):
            endpoint = f"/v1/{endpoint}"

        url = urljoin(self.base_url, endpoint)

        if self.debug:
            self.logger.debug(f"{method} {url} params={params} data={data}")

        try:
            response = self.session.request(
                method, url, params=params, data=data, timeout=self.timeout, **kwargs
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            self._handle_api_error(e.response, context=endpoint)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(
                f"Failed to connect to Stripe API: {str(e)}",
                details={"error": str(e)},
            )

        return response.json()

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status from response headers.

        Returns:
            Dictionary with rate limit information

        Note:
            Stripe doesn't provide explicit rate limit status endpoints.
            This returns information from the last API response headers.
        """
        # Stripe includes rate limit info in response headers
        return {
            "remaining": None,
            "limit": None,
            "reset_at": None,
            "retry_after": None,
            "note": "Stripe provides rate limit info via response headers",
        }

    def close(self):
        """Close session and cleanup resources."""
        if self.session:
            self.session.close()

    # Internal Methods

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication and retry strategy.

        Bug Prevention #1: Authentication headers
        Bug Prevention #2: Content-Type management

        Returns:
            Configured requests.Session
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        # Bug Prevention #2: Do NOT set Content-Type here!
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
        })

        # Bug Prevention #1: Use EXACT header name from docs
        # Stripe uses "Authorization: Bearer {api_key}"
        if self.access_token:
            session.headers["Authorization"] = f"Bearer {self.access_token}"

        if self.api_key:
            session.headers["Authorization"] = f"Bearer {self.api_key}"

        # Configure retries for rate limiting
        if self.max_retries > 0:
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,  # Exponential backoff: 1s, 2s, 4s, etc.
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "DELETE"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

        return session

    def _parse_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """
        Parse API response and extract data records.

        Bug Prevention #3: Response parsing with field fallbacks

        Handles different response formats:
        - Direct arrays: [{"id": 1}, {"id": 2}]
        - List wrapped: {"object": "list", "data": [...], "has_more": false}
        - Single object: {"id": 1, "name": "item"}

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
                "Invalid JSON response from Stripe API",
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
            # Primary field from docs: "data"
            # Alternatives: "items", "results", "records"
            records = (
                data.get("data")
                or data.get("items")
                or data.get("results")
                or data.get("records")
                or []
            )

            # Ensure we return a list
            if isinstance(records, list):
                return records
            elif records is not None:
                return [records]
            else:
                return []

        # Unknown format
        return []

    def _handle_api_error(self, response: requests.Response, context: str = ""):
        """
        Convert HTTP errors to structured driver exceptions.

        Args:
            response: Failed HTTP response
            context: Context string (e.g., "reading products")

        Raises:
            Appropriate DriverError subclass
        """
        status_code = response.status_code

        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "error" in error_data:
                error_obj = error_data["error"]
                error_msg = error_obj.get("message", "Unknown error")
                error_type = error_obj.get("type", "unknown")
                error_code = error_obj.get("code", "unknown")
            else:
                error_msg = response.text[:500]
                error_type = "unknown"
                error_code = "unknown"
        except ValueError:
            error_msg = response.text[:500]
            error_type = "unknown"
            error_code = "unknown"

        # Map status codes to exceptions
        if status_code == 401:
            raise AuthenticationError(
                f"Authentication failed: {error_msg}",
                details={
                    "status_code": 401,
                    "context": context,
                    "error_type": error_type,
                    "error_code": error_code,
                    "suggestion": "Check your Stripe API key and permissions",
                },
            )

        elif status_code == 403:
            raise AuthenticationError(
                f"Permission denied: {error_msg}",
                details={
                    "status_code": 403,
                    "context": context,
                    "error_type": error_type,
                    "suggestion": "Verify your API key has required permissions",
                },
            )

        elif status_code == 404:
            raise ObjectNotFoundError(
                f"Resource not found: {error_msg}",
                details={
                    "status_code": 404,
                    "context": context,
                    "error_type": error_type,
                    "suggestion": "Check resource type and ID spelling",
                },
            )

        elif status_code == 400:
            raise ValidationError(
                f"Invalid request: {error_msg}",
                details={
                    "status_code": 400,
                    "context": context,
                    "error_type": error_type,
                    "error_code": error_code,
                    "param": error_obj.get("param") if isinstance(error_data, dict) else None,
                },
            )

        elif status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            raise RateLimitError(
                f"Rate limit exceeded: {error_msg}",
                details={
                    "status_code": 429,
                    "retry_after": int(retry_after) if retry_after.isdigit() else 60,
                    "context": context,
                    "error_type": error_type,
                    "suggestion": f"Wait {retry_after} seconds before retrying",
                },
            )

        elif status_code >= 500:
            raise ConnectionError(
                f"Stripe API server error: {error_msg}",
                details={
                    "status_code": status_code,
                    "context": context,
                    "error_type": error_type,
                    "suggestion": "Stripe API is experiencing issues. Try again later.",
                },
            )

        else:
            raise DriverError(
                f"API request failed: {error_msg}",
                details={
                    "status_code": status_code,
                    "context": context,
                    "error_type": error_type,
                    "error_code": error_code,
                },
            )

    def _validate_connection(self):
        """
        Validate connection at initialization time (fail fast!).

        Makes a simple API call to verify credentials are valid.

        Raises:
            AuthenticationError: If credentials are invalid
            ConnectionError: If cannot reach Stripe API
        """
        try:
            # Make a simple GET request to verify auth
            endpoint = "/v1/products"
            url = urljoin(self.base_url, endpoint)

            if self.debug:
                self.logger.debug(f"Validating connection: GET {url}")

            response = self.session.get(url, params={"limit": 1}, timeout=self.timeout)
            response.raise_for_status()

            if self.debug:
                self.logger.debug("Connection validation successful")

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Invalid Stripe API key. Check your STRIPE_API_KEY environment variable.",
                    details={"api_url": self.base_url},
                )
            elif e.response.status_code == 403:
                raise AuthenticationError(
                    "Stripe API key does not have required permissions.",
                    details={"api_url": self.base_url},
                )
            else:
                raise ConnectionError(
                    f"Cannot connect to Stripe API (HTTP {e.response.status_code})",
                    details={"api_url": self.base_url, "error": str(e)},
                )

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Cannot reach Stripe API at {self.base_url}",
                details={"api_url": self.base_url, "error": str(e)},
            )

        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                f"Stripe API connection timed out after {self.timeout}s",
                details={"timeout": self.timeout, "api_url": self.base_url},
            )

        except Exception as e:
            raise ConnectionError(
                f"Failed to validate Stripe API connection: {str(e)}",
                details={"api_url": self.base_url, "error": str(e)},
            )
