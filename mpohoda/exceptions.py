"""
mPOHODA Driver Exception Hierarchy

Structured exceptions that provide clear, actionable error messages for agents.
Each exception includes a message and detailed information for programmatic handling.
"""

from typing import Dict, Any, Optional


class DriverError(Exception):
    """
    Base exception for all driver errors.

    All driver exceptions inherit from this to provide consistent error handling.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize driver error.

        Args:
            message: Clear error message for agents
            details: Structured data for programmatic error handling
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        """Return descriptive error message for agent."""
        return f"{self.__class__.__name__}: {self.message}"


class AuthenticationError(DriverError):
    """
    Invalid credentials or API key.

    Agent should:
    - Inform user to check credentials
    - Check .env file exists and has correct keys
    - Verify API key is still valid

    Example:
        AuthenticationError(
            "Invalid API key. Check your MPOHODA_API_KEY environment variable.",
            details={"required_env_vars": ["MPOHODA_API_KEY"]}
        )
    """

    pass


class ConnectionError(DriverError):
    """
    Cannot reach API (network issue, API down).

    Agent should:
    - Inform user API is unreachable
    - Suggest checking api_url configuration
    - Wait and retry later

    Example:
        ConnectionError(
            "Cannot reach mPOHODA API at https://api.mpohoda.cz",
            details={"api_url": "https://api.mpohoda.cz", "reason": "connection timeout"}
        )
    """

    pass


class ObjectNotFoundError(DriverError):
    """
    Requested object/resource doesn't exist.

    Agent should:
    - Call list_objects() to see what's available
    - Suggest similar object names (fuzzy match)

    Example:
        ObjectNotFoundError(
            "Object 'Leads' not found. Did you mean 'Activities'?",
            details={
                "requested": "Leads",
                "suggestions": ["Activities", "BusinessPartners"],
                "available": ["Activities", "BusinessPartners", "Banks", ...]
            }
        )
    """

    pass


class FieldNotFoundError(DriverError):
    """
    Requested field doesn't exist on object.

    Agent should:
    - Call get_fields(object_name) to see available fields
    - Suggest similar field names

    Example:
        FieldNotFoundError(
            "Field 'Email' not found on BusinessPartner",
            details={"object": "BusinessPartner", "field": "Email", "available_fields": [...]}
        )
    """

    pass


class QuerySyntaxError(DriverError):
    """
    Invalid query syntax.

    Agent should:
    - Fix query syntax based on error message
    - Consult driver README for query syntax rules
    - Regenerate query

    Example:
        QuerySyntaxError(
            "Invalid query: 'PageSize' parameter cannot exceed 50",
            details={"query": "...", "issue": "PageSize value too large"}
        )
    """

    pass


class RateLimitError(DriverError):
    """
    API rate limit exceeded (after automatic retries).

    Driver automatically retries with exponential backoff.
    This exception is only raised after max_retries exhausted.

    Agent should:
    - Inform user of rate limit
    - Suggest reducing batch size or adding delays
    - Show retry_after seconds

    Example:
        RateLimitError(
            "mPOHODA API rate limit exceeded. Retry after 60 seconds.",
            details={
                "retry_after": 60,
                "limit": 8000,
                "limit_type": "monthly",
                "reset_at": "2025-12-01T00:00:00Z",
                "attempts": 3
            }
        )
    """

    pass


class ValidationError(DriverError):
    """
    Data validation failed (for write operations).

    Note: Driver does NOT validate input by default.
    This is only raised when API returns validation errors or
    driver detects invalid parameters (e.g., page_size too large).

    Agent should:
    - Check required fields are present
    - Fix data types
    - Verify parameter constraints
    - Regenerate request

    Example:
        ValidationError(
            "page_size cannot exceed 50 (got: 100)",
            details={
                "parameter": "page_size",
                "provided": 100,
                "maximum": 50,
                "suggestion": "Use page_size <= 50"
            }
        )
    """

    pass


class TimeoutError(DriverError):
    """
    Request timed out.

    Agent should:
    - Inform user
    - Suggest increasing timeout parameter
    - Retry with smaller dataset

    Example:
        TimeoutError(
            "Request to /Activities timed out after 30 seconds",
            details={"endpoint": "/Activities", "timeout": 30}
        )
    """

    pass


class NotImplementedError(DriverError):
    """
    Operation not supported by this driver.

    Agent should:
    - Check driver capabilities with get_capabilities()
    - Use alternative operation or driver
    - Inform user of limitation

    Example:
        NotImplementedError(
            "Update operations not supported by mPOHODA driver. Use create/delete instead.",
            details={"operation": "update", "reason": "API returns 405 Method Not Allowed"}
        )
    """

    pass
