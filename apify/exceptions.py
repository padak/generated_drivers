"""
Apify Driver Exception Hierarchy

Structured exceptions for agent integration and programmatic error handling.
All exceptions include actionable error messages and structured details dict.
"""

from typing import Dict, Any, Optional


class DriverError(Exception):
    """
    Base exception for all driver errors.

    Provides structured error information for agent understanding and processing.
    All driver exceptions inherit from this base class.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize driver error.

        Args:
            message: Clear, actionable error message for agent
            details: Structured data dict for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        """Return descriptive error message"""
        return f"{self.__class__.__name__}: {self.message}"


class AuthenticationError(DriverError):
    """
    Invalid credentials or API key.

    Raised when:
    - API token is missing or invalid
    - Authentication header format is wrong
    - Token has expired or been revoked

    Agent should:
    - Check API token is set in environment variables
    - Verify token at: https://console.apify.com/settings/integrations
    - Check token has required permissions
    """

    pass


class ConnectionError(DriverError):
    """
    Cannot reach API (network issue, API down, invalid URL).

    Raised when:
    - Network is unreachable
    - API server is down or returning 5xx errors
    - Base URL is invalid or unreachable

    Agent should:
    - Check internet connection
    - Verify API is reachable: https://api.apify.com/v2
    - Suggest checking api_url configuration
    - Retry with exponential backoff
    """

    pass


class ObjectNotFoundError(DriverError):
    """
    Requested object/resource doesn't exist.

    Raised when:
    - Actor ID not found (HTTP 404)
    - Dataset ID not found
    - Run ID not found
    - Resource path is invalid

    Agent should:
    - Verify resource ID is correct
    - Call list_objects() or list_resources() to see available options
    - Suggest similar names via fuzzy matching
    """

    pass


class FieldNotFoundError(DriverError):
    """
    Requested field doesn't exist on object.

    Raised when:
    - Field name doesn't exist in response schema
    - Typo in field name

    Agent should:
    - Call get_fields(object_name) to see available fields
    - Suggest similar field names
    """

    pass


class QuerySyntaxError(DriverError):
    """
    Invalid query syntax or parameters.

    Raised when:
    - Query parameters are malformed (HTTP 400: invalid-request)
    - Required parameters are missing
    - Parameter values have invalid format

    Agent should:
    - Review query parameters against API documentation
    - Check parameter types and formats
    - Regenerate query with correct syntax
    """

    pass


class RateLimitError(DriverError):
    """
    API rate limit exceeded (after automatic retries).

    Raised when:
    - HTTP 429 error received (rate-limit-exceeded)
    - All retry attempts exhausted (default: 3 retries with exponential backoff)

    Driver automatically retries with exponential backoff before raising this.

    Agent should:
    - Inform user of rate limit
    - Show retry_after seconds from error details
    - Suggest reducing batch size or request frequency
    - Implement client-side delays between requests
    """

    pass


class ValidationError(DriverError):
    """
    Data validation failed (for write operations).

    Raised when:
    - Required fields are missing in create/update payload
    - Field values have invalid types
    - Field values exceed documented constraints
    - API validation fails

    Agent should:
    - Check required fields are present
    - Fix data types
    - Verify field values match constraints
    - Regenerate create/update call with valid data
    """

    pass


class TimeoutError(DriverError):
    """
    Request timed out.

    Raised when:
    - Request exceeds timeout value (default: 30 seconds)
    - No response received within timeout window

    Agent should:
    - Inform user request timed out
    - Suggest increasing timeout parameter if legitimate
    - Retry request (may be temporary network issue)
    - Consider splitting large requests into smaller chunks
    """

    pass


class NotImplementedError(DriverError):
    """
    Operation not supported by this driver.

    Raised when:
    - Operation requires capability not supported by API
    - Method is intentionally not implemented in driver

    Agent should:
    - Check driver capabilities before generating code
    - Use available operations instead
    - Inform user of limitation
    """

    pass
