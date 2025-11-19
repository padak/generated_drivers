"""
Odoo External RPC API Driver

A production-grade Python driver for the Odoo External RPC API (JSON-RPC 2.0).

Features:
- Bearer token authentication via API keys
- Full CRUD operations on any Odoo model
- Odoo Domain Language for powerful filtering
- Batch operations with automatic retry
- Field introspection and schema discovery
- Comprehensive error handling

Example:
    from odoo_driver import OdooDriver

    # Initialize from environment variables
    client = OdooDriver.from_env()

    # Discover available models
    models = client.list_objects()

    # Query data using Odoo Domain Language
    partners = client.read("[['active', '=', True]]", limit=50)

    # Cleanup
    client.close()
"""

import os
import time
import logging
import json
from typing import List, Dict, Any, Optional, Iterator
from urllib.parse import urljoin

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError as e:
    raise ImportError(
        "requests library is required. Install with: pip install requests"
    ) from e

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
        TimeoutError,
    )
except ImportError:
    # Fallback for standalone usage (e.g., direct test execution)
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


class OdooDriver(BaseDriver):
    """
    Odoo External RPC API Driver

    A comprehensive driver for Odoo's JSON-RPC 2.0 API with:
    - Bearer token authentication (API keys)
    - Full CRUD operations
    - Odoo Domain Language filtering
    - Batch operations with pagination
    - Schema discovery via ir.model and ir.model.fields
    - Automatic retry with exponential backoff

    Attributes:
        base_url: Odoo instance URL
        api_key: User's API key for authentication
        database: Odoo database name
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        debug: Enable debug logging
        session: Reusable requests.Session for connection pooling
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        database: str,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        **kwargs
    ):
        """
        Initialize OdooDriver.

        CRITICAL: This follows strict 4-phase initialization order.
        See bug prevention requirements in driver specification.

        Args:
            base_url: Odoo instance URL (e.g., https://odoo.example.com)
            api_key: User's API key for authentication (never hardcode!)
            database: Odoo database name
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts on rate limit (default: 3)
            debug: Enable debug logging (default: False)
            **kwargs: Additional options

        Raises:
            AuthenticationError: If credentials are invalid or missing
            ConnectionError: If cannot reach Odoo instance

        Example:
            >>> driver = OdooDriver(
            ...     base_url="https://odoo.example.com",
            ...     api_key="user_api_key",
            ...     database="production",
            ...     debug=True
            ... )
        """

        # ===== PHASE 1: Set custom attributes =====
        # Initialize driver-specific attributes before parent attributes
        self.database = database
        self.driver_name = "OdooDriver"

        # Setup logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if debug else logging.WARNING)

        # ===== PHASE 2: Set parent class attributes =====
        # DO NOT call super().__init__()! Set these manually.
        # This must happen BEFORE _create_session() so session can use them.
        self.base_url = base_url.rstrip("/")  # Remove trailing slash
        self.api_key = api_key
        self.access_token = None  # Not used for Odoo, but part of contract
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
    def from_env(cls, **kwargs) -> "OdooDriver":
        """
        Create driver instance from environment variables.

        Environment variables:
            ODOO_BASE_URL: Odoo instance URL (e.g., https://odoo.example.com)
            ODOO_DATABASE: Database name
            ODOO_API_KEY: User's API key

        Args:
            **kwargs: Additional arguments passed to __init__

        Returns:
            Configured OdooDriver instance

        Raises:
            AuthenticationError: If required env vars are missing

        Example:
            >>> driver = OdooDriver.from_env()
            >>> models = driver.list_objects()
        """
        base_url = os.getenv("ODOO_BASE_URL")
        database = os.getenv("ODOO_DATABASE")
        api_key = os.getenv("ODOO_API_KEY")

        # Bug Prevention #6: Never hardcode credentials
        missing_vars = []
        if not base_url:
            missing_vars.append("ODOO_BASE_URL")
        if not database:
            missing_vars.append("ODOO_DATABASE")
        if not api_key:
            missing_vars.append("ODOO_API_KEY")

        if missing_vars:
            raise AuthenticationError(
                f"Missing required environment variables: {', '.join(missing_vars)}",
                details={
                    "required_env_vars": ["ODOO_BASE_URL", "ODOO_DATABASE", "ODOO_API_KEY"],
                    "missing": missing_vars,
                    "example": {
                        "ODOO_BASE_URL": "https://odoo.example.com",
                        "ODOO_DATABASE": "production",
                        "ODOO_API_KEY": "user_api_key_here"
                    }
                }
            )

        return cls(
            base_url=base_url,
            database=database,
            api_key=api_key,
            **kwargs
        )

    def get_capabilities(self) -> DriverCapabilities:
        """
        Return driver capabilities.

        Returns:
            DriverCapabilities indicating full CRUD + batch operations support

        Example:
            >>> capabilities = driver.get_capabilities()
            >>> print(capabilities.query_language)
            'Odoo Domain Language'
        """
        return DriverCapabilities(
            read=True,
            write=True,
            update=True,
            delete=True,
            batch_operations=True,
            streaming=False,
            pagination=PaginationStyle.OFFSET,
            query_language="Odoo Domain Language",
            max_page_size=1000,
            supports_transactions=False,
            supports_relationships=True
        )

    # ===== Discovery Methods =====

    def list_objects(self) -> List[str]:
        """
        Discover all available Odoo models.

        Queries ir.model to get all installed models in the database.

        Returns:
            List of model names (e.g., ["res.partner", "sale.order", "res.users"])

        Raises:
            ConnectionError: If API request fails

        Example:
            >>> models = driver.list_objects()
            >>> print(models[:5])
            ['res.partner', 'res.users', 'res.company', 'sale.order', 'purchase.order']
        """
        try:
            # Search all models in the database
            domain = "[]"  # Empty domain = all records
            results = self.read(
                query=domain,
                limit=None  # Get all models
            )

            if not results:
                # Fallback: query ir.model directly
                results = self._execute_kw(
                    model="ir.model",
                    method="search_read",
                    args=[[], ["model", "name"]],
                    kwargs={}
                )

            # Extract model names
            models = []
            for record in results:
                if "model" in record:
                    models.append(record["model"])

            return sorted(models)

        except Exception as e:
            raise ConnectionError(
                f"Failed to list Odoo models: {str(e)}",
                details={"error": str(e), "database": self.database}
            )

    def get_fields(self, object_name: str) -> Dict[str, Any]:
        """
        Get complete field schema for an Odoo model.

        Queries ir.model.fields to get all field definitions and metadata.

        Args:
            object_name: Odoo model name (e.g., "res.partner")

        Returns:
            Dictionary mapping field names to field metadata:
            {
                "field_name": {
                    "type": "char|integer|float|boolean|date|datetime|text|many2one|one2many|many2many",
                    "label": "Human Readable Name",
                    "required": bool,
                    "readonly": bool,
                    "relation": "related_model" (for relational fields)
                }
            }

        Raises:
            ObjectNotFoundError: If model doesn't exist
            ConnectionError: If API request fails

        Example:
            >>> fields = driver.get_fields("res.partner")
            >>> print(fields["name"])
            {
                'type': 'char',
                'label': 'Name',
                'required': True,
                'readonly': False,
                'relation': None
            }
        """
        try:
            # Verify model exists
            if not self._model_exists(object_name):
                available = self.list_objects()
                suggestions = self._suggest_similar(object_name, available)
                raise ObjectNotFoundError(
                    f"Model '{object_name}' not found. Available models: {', '.join(available[:5])}...",
                    details={
                        "requested": object_name,
                        "suggestions": suggestions,
                        "available": available
                    }
                )

            # Query ir.model.fields for this model
            domain = f"[['model', '=', '{object_name}']]"
            fields_data = self._execute_kw(
                model="ir.model.fields",
                method="search_read",
                args=[[["model", "=", object_name]], ["name", "field_description", "ttype", "required", "readonly", "relation", "selection"]],
                kwargs={}
            )

            # Transform to driver format
            fields = {}
            for field in fields_data:
                fields[field["name"]] = {
                    "type": field["ttype"],
                    "label": field.get("field_description", field["name"]),
                    "required": field.get("required", False),
                    "readonly": field.get("readonly", False),
                    "relation": field.get("relation")
                }

            # Add automatic fields that Odoo always provides
            if "id" not in fields:
                fields["id"] = {
                    "type": "integer",
                    "label": "ID",
                    "required": True,
                    "readonly": True,
                    "relation": None
                }

            for auto_field in ["create_date", "write_date"]:
                if auto_field not in fields:
                    fields[auto_field] = {
                        "type": "datetime",
                        "label": auto_field.replace("_", " ").title(),
                        "required": False,
                        "readonly": True,
                        "relation": None
                    }

            return fields

        except ObjectNotFoundError:
            raise
        except Exception as e:
            raise ConnectionError(
                f"Failed to get fields for model '{object_name}': {str(e)}",
                details={"model": object_name, "error": str(e)}
            )

    # ===== Read Operations =====

    def read(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a read query using Odoo Domain Language and return results.

        Executes a search_read operation on a model using Odoo domain syntax.

        Args:
            query: Odoo domain string (e.g., "[['active', '=', True]]")
            limit: Maximum number of records to return (default: 80)
            offset: Number of records to skip (default: 0)

        Returns:
            List of record dictionaries with all fields

        Raises:
            QuerySyntaxError: Invalid domain syntax
            ConnectionError: If API request fails
            RateLimitError: If rate limited after retries

        Example:
            >>> # Find active partners
            >>> domain = "[['active', '=', True], ['customer', '=', True]]"
            >>> partners = driver.read(domain, limit=100)
            >>> print(len(partners))
            42

            >>> # With pagination
            >>> for batch in driver.read_batched(domain, batch_size=100):
            ...     process_batch(batch)
        """
        try:
            # Set defaults
            if limit is None:
                limit = 80  # Odoo default

            if offset is None:
                offset = 0

            # Parse and validate domain
            try:
                domain_list = json.loads(query) if isinstance(query, str) else query
            except json.JSONDecodeError as e:
                raise QuerySyntaxError(
                    f"Invalid domain syntax: {str(e)}",
                    details={
                        "query": query,
                        "error": str(e),
                        "example": "[['active', '=', True], ['name', 'ilike', '%john%']]"
                    }
                )

            # Validate domain structure
            self._validate_domain(domain_list)

            # Execute search_read
            results = self._execute_kw(
                model="res.partner",  # Default model for read
                method="search_read",
                args=[domain_list, []],  # Empty list = all fields
                kwargs={"limit": limit, "offset": offset}
            )

            return results

        except (QuerySyntaxError, ConnectionError, RateLimitError):
            raise
        except Exception as e:
            raise ConnectionError(
                f"Failed to read records: {str(e)}",
                details={"query": query, "error": str(e)}
            )

    def read_batched(
        self,
        query: str,
        batch_size: int = 80
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Execute query and yield results in batches (memory-efficient).

        Reads records in chunks using offset/limit pagination.

        Args:
            query: Odoo domain string
            batch_size: Number of records per batch (default: 80, max: 1000)

        Yields:
            Batches of record dictionaries

        Raises:
            QuerySyntaxError: Invalid domain syntax
            ConnectionError: If API request fails

        Example:
            >>> domain = "[['active', '=', True]]"
            >>> for batch in driver.read_batched(domain, batch_size=100):
            ...     print(f"Processing {len(batch)} records")
            ...     # Process batch...
        """
        if batch_size > 1000:
            raise ValueError(f"batch_size cannot exceed 1000 (got: {batch_size})")

        offset = 0
        while True:
            try:
                batch = self.read(query, limit=batch_size, offset=offset)

                if not batch:
                    # No more records
                    break

                yield batch

                if len(batch) < batch_size:
                    # Last batch (incomplete)
                    break

                offset += batch_size

            except Exception as e:
                self.logger.error(f"Error reading batch at offset {offset}: {e}")
                raise

    # ===== Write Operations =====

    def create(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new Odoo record.

        Args:
            object_name: Model name (e.g., "res.partner")
            data: Field values as dictionary

        Returns:
            Created record data with ID

        Raises:
            ObjectNotFoundError: If model doesn't exist
            ValidationError: If validation fails
            ConnectionError: If API request fails

        Example:
            >>> record = driver.create("res.partner", {
            ...     "name": "Acme Corporation",
            ...     "email": "info@acme.com",
            ...     "customer": True
            ... })
            >>> print(record["id"])
            42
        """
        try:
            if not self._model_exists(object_name):
                raise ObjectNotFoundError(
                    f"Model '{object_name}' not found",
                    details={"model": object_name}
                )

            # Execute create
            record_id = self._execute_kw(
                model=object_name,
                method="create",
                args=[data],
                kwargs={}
            )

            # Read created record to return full data
            created_record = self._execute_kw(
                model=object_name,
                method="read",
                args=[[record_id], []],
                kwargs={}
            )

            return created_record[0] if created_record else {"id": record_id, **data}

        except ObjectNotFoundError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            if "validation" in str(e).lower():
                raise ValidationError(
                    f"Validation failed when creating {object_name}: {str(e)}",
                    details={"model": object_name, "data": data, "error": str(e)}
                )
            raise ConnectionError(
                f"Failed to create record in {object_name}: {str(e)}",
                details={"model": object_name, "error": str(e)}
            )

    def update(self, object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Odoo record.

        Args:
            object_name: Model name
            record_id: Record ID to update
            data: Field values to update

        Returns:
            Updated record data

        Raises:
            ObjectNotFoundError: If model or record doesn't exist
            ValidationError: If validation fails
            ConnectionError: If API request fails

        Example:
            >>> driver.update("res.partner", 42, {
            ...     "email": "newemail@acme.com"
            ... })
        """
        try:
            if not self._model_exists(object_name):
                raise ObjectNotFoundError(f"Model '{object_name}' not found")

            # Convert record_id to integer
            try:
                record_id_int = int(record_id)
            except ValueError:
                raise ValidationError(
                    f"Invalid record ID: {record_id}",
                    details={"record_id": record_id}
                )

            # Execute update (write in Odoo)
            self._execute_kw(
                model=object_name,
                method="write",
                args=[[record_id_int], data],
                kwargs={}
            )

            # Read updated record
            updated = self._execute_kw(
                model=object_name,
                method="read",
                args=[[record_id_int], []],
                kwargs={}
            )

            return updated[0] if updated else {"id": record_id_int, **data}

        except (ObjectNotFoundError, ValidationError):
            raise
        except Exception as e:
            raise ConnectionError(
                f"Failed to update record {record_id} in {object_name}: {str(e)}",
                details={"model": object_name, "record_id": record_id, "error": str(e)}
            )

    def delete(self, object_name: str, record_id: str) -> bool:
        """
        Delete an Odoo record.

        CAUTION: Deletion is permanent. Agents should require explicit approval.

        Args:
            object_name: Model name
            record_id: Record ID to delete

        Returns:
            True if successful

        Raises:
            ObjectNotFoundError: If model or record doesn't exist
            ConnectionError: If API request fails

        Example:
            >>> driver.delete("res.partner", 42)
            True
        """
        try:
            if not self._model_exists(object_name):
                raise ObjectNotFoundError(f"Model '{object_name}' not found")

            # Convert record_id to integer
            try:
                record_id_int = int(record_id)
            except ValueError:
                raise ValidationError(f"Invalid record ID: {record_id}")

            # Execute delete (unlink in Odoo)
            self._execute_kw(
                model=object_name,
                method="unlink",
                args=[[record_id_int]],
                kwargs={}
            )

            return True

        except (ObjectNotFoundError, ValidationError):
            raise
        except Exception as e:
            raise ConnectionError(
                f"Failed to delete record {record_id} from {object_name}: {str(e)}",
                details={"model": object_name, "record_id": record_id, "error": str(e)}
            )

    # ===== Internal Methods =====

    def _create_session(self) -> requests.Session:
        """
        Create HTTP session with authentication and retry strategy.

        Bug Prevention #1 & #2: Correct authentication header setup.

        Returns:
            Configured requests.Session with auth headers
        """
        session = requests.Session()

        # Set headers that apply to ALL requests
        session.headers.update({
            "Accept": "application/json",
            "User-Agent": f"{self.driver_name}-Python-Driver/1.0.0",
        })
        # NOTE: Do NOT set Content-Type here! (Bug Prevention #2)
        # requests library adds it automatically for POST requests

        # Bug Prevention #1: Set EXACT authentication header name from docs
        if self.api_key:
            session.headers["Authorization"] = f"Bearer {self.api_key}"

        # Configure retries (automatic exponential backoff)
        if self.max_retries > 0:
            retry_strategy = Retry(
                total=self.max_retries,
                backoff_factor=1,  # 1s, 2s, 4s, 8s...
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "PUT", "DELETE"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("https://", adapter)
            session.mount("http://", adapter)

        return session

    def _validate_connection(self):
        """
        Validate connection at initialization (fail fast!).

        Raises:
            AuthenticationError: If credentials invalid
            ConnectionError: If cannot reach Odoo instance
        """
        try:
            # Test connection by querying ir.model
            response = self._execute_kw(
                model="ir.model",
                method="search_read",
                args=[[], ["id"]],
                kwargs={"limit": 1}
            )

            if self.debug:
                self.logger.debug(f"Connection validated. Found {len(response)} models.")

        except Exception as e:
            error_str = str(e)

            if "401" in error_str or "Unauthorized" in error_str:
                raise AuthenticationError(
                    "Invalid API key or credentials. Check ODOO_API_KEY environment variable.",
                    details={
                        "base_url": self.base_url,
                        "database": self.database,
                        "error": error_str
                    }
                )

            if "Connection" in error_str or "Cannot reach" in error_str:
                raise ConnectionError(
                    f"Cannot reach Odoo instance at {self.base_url}",
                    details={
                        "base_url": self.base_url,
                        "error": error_str
                    }
                )

            raise ConnectionError(
                f"Connection validation failed: {error_str}",
                details={
                    "base_url": self.base_url,
                    "database": self.database,
                    "error": error_str
                }
            )

    def _execute_kw(
        self,
        model: str,
        method: str,
        args: List[Any],
        kwargs: Dict[str, Any]
    ) -> Any:
        """
        Execute a keyword method on an Odoo model via JSON-RPC.

        This is the core method for all API calls to Odoo.

        Args:
            model: Model name (e.g., "res.partner")
            method: Method name (e.g., "search_read", "create", "write")
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method

        Returns:
            Method result

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If request fails
            RateLimitError: If rate limited
        """
        url = urljoin(self.base_url, "/api/v1/call")

        # Build JSON-RPC request
        request_payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [self.database, self.api_key, model, method, args, kwargs]
            },
            "id": 1
        }

        if self.debug:
            self.logger.debug(f"Request: {model}.{method} - {request_payload}")

        try:
            response = self.session.post(
                url,
                json=request_payload,
                timeout=self.timeout
            )

            if self.debug:
                self.logger.debug(f"Response status: {response.status_code}")

            # Bug Prevention #3: Parse response with field fallbacks
            response_data = self._parse_response(response)

            if self.debug:
                self.logger.debug(f"Response data: {response_data}")

            return response_data

        except requests.exceptions.Timeout:
            raise TimeoutError(
                f"Request timed out after {self.timeout} seconds",
                details={
                    "timeout": self.timeout,
                    "model": model,
                    "method": method
                }
            )
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Connection error: {str(e)}",
                details={"error": str(e), "url": url}
            )
        except Exception as e:
            raise ConnectionError(
                f"Request failed: {str(e)}",
                details={"error": str(e), "model": model, "method": method}
            )

    def _parse_response(self, response: requests.Response) -> Any:
        """
        Parse Odoo JSON-RPC response.

        Bug Prevention #3: Handle case-sensitive field names with fallbacks.

        Args:
            response: HTTP response from Odoo

        Returns:
            Response data

        Raises:
            AuthenticationError: If authentication failed
            RateLimitError: If rate limited
            ConnectionError: If response is invalid
        """
        try:
            data = response.json()
        except ValueError as e:
            raise ConnectionError(
                f"Invalid JSON response: {str(e)}",
                details={
                    "status_code": response.status_code,
                    "content": response.text[:500]
                }
            )

        if self.debug:
            self.logger.debug(f"Parsed response: {data}")

        # Handle HTTP error status codes
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed (401). Check API key.",
                details={"status_code": 401}
            )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(
                f"Rate limited. Retry after {retry_after} seconds.",
                details={"retry_after": retry_after, "status_code": 429}
            )

        if response.status_code >= 500:
            raise ConnectionError(
                f"Server error ({response.status_code}): {response.text[:200]}",
                details={"status_code": response.status_code}
            )

        # Check for JSON-RPC error in response
        if isinstance(data, dict):
            if "error" in data and data["error"] is not None:
                error_info = data["error"]
                error_msg = error_info.get("message", "Unknown error")
                error_code = error_info.get("code", "unknown")

                if "AccessDenied" in error_msg or "Access denied" in error_msg:
                    raise AuthenticationError(
                        f"Access denied: {error_msg}",
                        details={"error_code": error_code, "error_msg": error_msg}
                    )

                raise ConnectionError(
                    f"Odoo error: {error_msg}",
                    details={
                        "error_code": error_code,
                        "error_msg": error_msg,
                        "error_data": error_info.get("data")
                    }
                )

            # Extract result field (case-sensitive!)
            if "result" in data:
                return data["result"]

            # Fallback: try other common field names
            if "data" in data:
                return data["data"]

            if "items" in data:
                return data["items"]

            # No recognized data field
            return data

        # Handle direct list/value responses
        return data

    def _model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists in Odoo.

        Args:
            model_name: Model name to check

        Returns:
            True if model exists, False otherwise
        """
        try:
            result = self._execute_kw(
                model="ir.model",
                method="search_read",
                args=[[["model", "=", model_name]], ["id"]],
                kwargs={"limit": 1}
            )
            return bool(result)
        except Exception:
            return False

    def _validate_domain(self, domain: Any) -> None:
        """
        Validate Odoo domain syntax.

        Args:
            domain: Domain to validate

        Raises:
            QuerySyntaxError: If domain is invalid
        """
        if not isinstance(domain, list):
            raise QuerySyntaxError(
                "Domain must be a list",
                details={
                    "domain": domain,
                    "expected_type": "list",
                    "example": "[['name', '=', 'John']]"
                }
            )

        # Basic validation of domain structure
        for condition in domain:
            if isinstance(condition, str) and condition in ["&", "|", "!"]:
                # Logical operator
                continue
            elif isinstance(condition, (list, tuple)):
                # Field condition
                if len(condition) != 3:
                    raise QuerySyntaxError(
                        f"Domain condition must have 3 elements [field, operator, value], got {len(condition)}",
                        details={
                            "condition": condition,
                            "length": len(condition),
                            "example": "['name', '=', 'John']"
                        }
                    )
            else:
                raise QuerySyntaxError(
                    f"Invalid domain element: {condition}",
                    details={
                        "element": condition,
                        "type": type(condition).__name__
                    }
                )

    def _suggest_similar(self, requested: str, available: List[str], max_suggestions: int = 3) -> List[str]:
        """
        Suggest similar model names using simple string matching.

        Args:
            requested: Requested model name
            available: List of available models
            max_suggestions: Maximum suggestions to return

        Returns:
            List of similar model names
        """
        import difflib

        # Find close matches
        matches = difflib.get_close_matches(
            requested,
            available,
            n=max_suggestions,
            cutoff=0.6
        )

        return matches

    def close(self):
        """
        Close session and cleanup resources.

        Example:
            >>> driver = OdooDriver.from_env()
            >>> try:
            ...     data = driver.read("[['active', '=', True]]")
            ... finally:
            ...     driver.close()
        """
        if hasattr(self, "session") and self.session:
            self.session.close()
            if self.debug:
                self.logger.debug("Session closed")
