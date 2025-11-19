"""
Odoo Driver Exception Hierarchy

Structured exceptions for all driver errors, enabling agents to understand and react to failures.
"""

from typing import Any, Optional, Dict


class DriverError(Exception):
    """
    Base exception for all Odoo driver errors.

    All driver-specific exceptions inherit from this class and include:
    - Clear message for debugging
    - Details dict for programmatic handling
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize DriverError.

        Args:
            message: Human-readable error description
            details: Dictionary with structured error context
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
    - Check API key is set correctly
    - Verify API key is not expired
    - Check environment variables (ODOO_API_KEY, ODOO_BASE_URL)
    - Verify user has API access permission in Odoo

    Example:
        AuthenticationError(
            "Invalid API key. Verify ODOO_API_KEY environment variable is set.",
            details={"env_vars": ["ODOO_API_KEY", "ODOO_BASE_URL", "ODOO_DATABASE"]}
        )
    """

    pass


class ConnectionError(DriverError):
    """
    Cannot reach Odoo instance (network issue, server down).

    Agent should:
    - Check base URL is correct and reachable
    - Verify Odoo instance is running
    - Check network connectivity
    - Wait and retry later

    Example:
        ConnectionError(
            "Cannot reach Odoo instance at https://odoo.example.com",
            details={"base_url": "https://odoo.example.com", "timeout": 30}
        )
    """

    pass


class ObjectNotFoundError(DriverError):
    """
    Requested model/object doesn't exist in Odoo.

    Agent should:
    - Call list_objects() to see available models
    - Suggest similar model names (fuzzy match)
    - Check spelling and case

    Example:
        ObjectNotFoundError(
            "Model 'res.partners' not found. Did you mean 'res.partner'?",
            details={
                "requested": "res.partners",
                "suggestions": ["res.partner", "res.partner.bank"],
                "available": ["res.partner", "res.users", "sale.order", ...]
            }
        )
    """

    pass


class FieldNotFoundError(DriverError):
    """
    Requested field doesn't exist on model.

    Agent should:
    - Call get_fields(model_name) to see available fields
    - Suggest similar field names
    - Check spelling

    Example:
        FieldNotFoundError(
            "Field 'email_address' not found on res.partner. Did you mean 'email'?",
            details={
                "model": "res.partner",
                "requested": "email_address",
                "suggestions": ["email", "email_cc", "email_formatted"],
                "available": ["name", "email", "phone", "mobile", ...]
            }
        )
    """

    pass


class QuerySyntaxError(DriverError):
    """
    Invalid domain or query syntax.

    Agent should:
    - Review domain syntax in README
    - Check operators and field names
    - Validate domain structure

    Example:
        QuerySyntaxError(
            "Invalid domain syntax: missing operator in condition",
            details={
                "domain": "[['name', 'John']]",
                "error": "Condition must have 3 elements: [field, operator, value]",
                "example": "[['name', '=', 'John']]"
            }
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
    - Reduce batch size
    - Add delays between requests
    - Retry after specified interval

    Example:
        RateLimitError(
            "Rate limit exceeded after 3 retries. Retry after 60 seconds.",
            details={
                "retry_after": 60,
                "attempts": 3,
                "reset_at": "2025-11-19T15:30:00Z"
            }
        )
    """

    pass


class ValidationError(DriverError):
    """
    Data validation failed (for write operations).

    Driver does NOT validate input by default.
    This is raised when Odoo server returns validation errors.

    Agent should:
    - Check required fields are present
    - Fix data types
    - Verify field constraints

    Example:
        ValidationError(
            "Required field 'name' is missing",
            details={
                "model": "res.partner",
                "missing_fields": ["name"],
                "errors": {"name": "Field is required"}
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
    - Retry with smaller dataset or reduced batch size

    Example:
        TimeoutError(
            "Request timed out after 30 seconds",
            details={"timeout": 30, "suggestion": "Increase timeout or reduce batch size"}
        )
    """

    pass
