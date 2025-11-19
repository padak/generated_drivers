"""
PostHog Driver Exception Hierarchy

Provides structured exceptions that agents can understand and react to.
All exceptions include:
- Clear message describing what went wrong
- Actionable suggestions for fixing the error
- details dict with structured data for programmatic handling
"""

from typing import Any, Dict, Optional


class DriverError(Exception):
    """
    Base exception for all PostHog driver errors.

    All driver exceptions inherit from this class and provide:
    - message: Human-readable description of the error
    - details: Dictionary with structured error information

    Example:
        try:
            driver.read("SELECT * FROM events")
        except DriverError as e:
            print(f"Error: {e.message}")
            print(f"Details: {e.details}")
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize driver error.

        Args:
            message: Human-readable error description
            details: Optional dictionary with structured error information
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

    Raised when:
    - API key is missing or empty
    - Access token is invalid
    - Credentials are expired
    - Insufficient permissions for the requested scope

    Agent should:
    - Check credentials are correct
    - Verify API key has required scopes
    - Check .env file exists and has correct variables

    Example:
        AuthenticationError(
            "Invalid PostHog API key. Set POSTHOG_API_KEY environment variable.",
            details={
                "required_env_vars": ["POSTHOG_API_KEY"],
                "api_url": "https://app.posthog.com"
            }
        )
    """

    pass


class ConnectionError(DriverError):
    """
    Cannot reach PostHog API (network issue, API down).

    Raised when:
    - Network timeout
    - API server is unreachable
    - DNS resolution fails
    - SSL/TLS certificate issues

    Agent should:
    - Inform user API is unreachable
    - Suggest checking network connectivity
    - Suggest checking api_url configuration
    - Wait and retry later

    Example:
        ConnectionError(
            "Cannot reach PostHog API at https://app.posthog.com. Connection timeout.",
            details={
                "api_url": "https://app.posthog.com",
                "timeout": 30,
                "suggestion": "Check your internet connection or try again later"
            }
        )
    """

    pass


class ObjectNotFoundError(DriverError):
    """
    Requested object/resource doesn't exist.

    Raised when:
    - Dashboard ID not found
    - Dataset doesn't exist
    - Batch export ID is invalid
    - User ID not found

    Agent should:
    - Call list_objects() to see what's available
    - Suggest similar object names (fuzzy match)
    - Ask user to verify the ID

    Example:
        ObjectNotFoundError(
            "Dashboard 'xyz123' not found.",
            details={
                "requested_id": "xyz123",
                "available_types": ["dashboards", "datasets", "batch_exports"],
                "suggestion": "Use list_objects() to find available resources"
            }
        )
    """

    pass


class FieldNotFoundError(DriverError):
    """
    Requested field doesn't exist on object/resource.

    Raised when:
    - Field name doesn't exist in dataset
    - Property name not found in event
    - Column name invalid for query

    Agent should:
    - Call get_fields(object_name) to see available fields
    - Suggest similar field names
    - Check for typos or case sensitivity

    Example:
        FieldNotFoundError(
            "Field 'email_address' not found on persons object.",
            details={
                "object": "persons",
                "requested_field": "email_address",
                "suggestions": ["email", "email_verified"]
            }
        )
    """

    pass


class QuerySyntaxError(DriverError):
    """
    Invalid query syntax or malformed request.

    Raised when:
    - HogQL query has syntax errors
    - Query references non-existent fields
    - Invalid filter syntax
    - Malformed request body

    Agent should:
    - Fix query syntax based on error message
    - Consult driver README for query language rules
    - Regenerate query with correct syntax

    Example:
        QuerySyntaxError(
            "HogQL syntax error: Unexpected token 'SELECT' at position 0",
            details={
                "query": "SELCT * FROM events",
                "error_position": 0,
                "suggestion": "Check query syntax in README"
            }
        )
    """

    pass


class RateLimitError(DriverError):
    """
    API rate limit exceeded (after automatic retries).

    Raised when:
    - Rate limit is exceeded after max_retries
    - Organization-wide limit reached
    - Request quota exhausted

    Driver automatically retries with exponential backoff.
    This exception is only raised after max_retries exhausted.

    Agent should:
    - Inform user of rate limit
    - Suggest reducing batch size or adding delays
    - Show retry_after seconds
    - Wait before retrying

    Example:
        RateLimitError(
            "PostHog API rate limit exceeded (480 req/min). Retry after 60 seconds.",
            details={
                "limit": 480,
                "period": "minute",
                "retry_after": 60,
                "reset_at": "2025-11-19T15:30:00Z",
                "suggestion": "Wait 60 seconds before retrying or reduce batch size"
            }
        )
    """

    pass


class ValidationError(DriverError):
    """
    Data validation failed (typically on write operations).

    Raised when:
    - Required field is missing
    - Field value has wrong type
    - Field value exceeds length limit
    - Invalid enum value provided
    - API returns validation error

    Agent should:
    - Check required fields are present
    - Verify field data types match schema
    - Fix data and retry
    - Call get_fields() to check schema

    Example:
        ValidationError(
            "Required field 'name' is missing on dashboard creation",
            details={
                "object": "dashboards",
                "operation": "create",
                "missing_fields": ["name"],
                "required_fields": ["name", "description"],
                "suggestion": "Provide a name for the dashboard"
            }
        )
    """

    pass


class TimeoutError(DriverError):
    """
    Request timed out.

    Raised when:
    - Request exceeds timeout threshold
    - No response from server within timeout period
    - Network is slow

    Agent should:
    - Inform user about timeout
    - Suggest increasing timeout parameter
    - Suggest retrying with smaller dataset
    - Check network connectivity

    Example:
        TimeoutError(
            "PostHog API request timed out after 30 seconds",
            details={
                "timeout": 30,
                "suggestion": "Try increasing timeout or reducing query scope"
            }
        )
    """

    pass
