"""
Example 6: Error handling - Gracefully handle various error conditions

This example demonstrates:
- Handling authentication errors
- Handling model/field not found errors
- Handling validation errors
- Handling rate limiting
- Graceful degradation
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import (
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    FieldNotFoundError,
    ValidationError,
    RateLimitError,
    QuerySyntaxError,
)


def example_1_authentication_error():
    """Handle authentication errors."""
    print("Example 1: Authentication Error\n")

    try:
        client = OdooDriver(
            base_url="https://odoo.example.com",
            database="production",
            api_key="invalid_key_12345",  # Invalid key
        )
    except AuthenticationError as e:
        print(f"✗ Authentication failed")
        print(f"  Message: {e.message}")
        print(f"  Details: {e.details}\n")


def example_2_model_not_found():
    """Handle model not found errors."""
    print("Example 2: Model Not Found\n")

    client = OdooDriver.from_env()

    try:
        # Try to access non-existent model
        fields = client.get_fields("non.existent.model")

    except ObjectNotFoundError as e:
        print(f"✗ Model not found")
        print(f"  Requested: {e.details.get('requested')}")
        print(f"  Suggestions: {e.details.get('suggestions', [])}")
        print(f"  Message: {e.message}\n")

    client.close()


def example_3_query_syntax_error():
    """Handle query syntax errors."""
    print("Example 3: Query Syntax Error\n")

    client = OdooDriver.from_env()

    try:
        # Invalid domain syntax (missing operator)
        results = client.read("[['name', 'John']]")

    except QuerySyntaxError as e:
        print(f"✗ Invalid query syntax")
        print(f"  Message: {e.message}")
        print(f"  Details: {e.details}\n")

    client.close()


def example_4_validation_error():
    """Handle validation errors."""
    print("Example 4: Validation Error\n")

    client = OdooDriver.from_env()

    try:
        # Try to create record with missing required field
        record = client.create("res.partner", {
            "email": "test@example.com",
            # Missing 'name' (required field)
        })

    except ValidationError as e:
        print(f"✗ Validation failed")
        print(f"  Message: {e.message}")
        print(f"  Missing fields: {e.details.get('missing_fields', [])}\n")

    except ObjectNotFoundError:
        print(f"  (Model check failed - skipping)\n")

    client.close()


def example_5_rate_limiting():
    """Handle rate limiting."""
    print("Example 5: Rate Limiting\n")

    client = OdooDriver.from_env()

    try:
        # Simulate rate limit by reading many times
        for i in range(5):
            results = client.read("[['active', '=', True]]", limit=1)
            print(f"  Request {i + 1}: OK")

    except RateLimitError as e:
        print(f"✗ Rate limited!")
        print(f"  Message: {e.message}")
        print(f"  Retry after: {e.details.get('retry_after', 'unknown')} seconds\n")

    client.close()


def example_6_graceful_fallback():
    """Gracefully handle errors with fallback."""
    print("Example 6: Graceful Fallback\n")

    client = OdooDriver.from_env()

    # Try to get fields for a model, with fallback
    models_to_try = ["res.partner", "non.existent", "res.users"]

    for model_name in models_to_try:
        try:
            fields = client.get_fields(model_name)
            print(f"  ✓ {model_name}: {len(fields)} fields")

        except ObjectNotFoundError as e:
            print(f"  ✗ {model_name}: Not found (trying next...)")

        except Exception as e:
            print(f"  ✗ {model_name}: Error - {e}")

    print()
    client.close()


def main():
    """Run all error handling examples."""

    print("=" * 60)
    print("Odoo Driver - Error Handling Examples")
    print("=" * 60)
    print()

    # Example 1: Skip (would require invalid credentials)
    # example_1_authentication_error()

    # Example 2: Model not found
    try:
        example_2_model_not_found()
    except Exception as e:
        print(f"  Error: {e}\n")

    # Example 3: Query syntax error
    try:
        example_3_query_syntax_error()
    except Exception as e:
        print(f"  Error: {e}\n")

    # Example 4: Validation error
    try:
        example_4_validation_error()
    except Exception as e:
        print(f"  Error: {e}\n")

    # Example 5: Rate limiting
    try:
        example_5_rate_limiting()
    except Exception as e:
        print(f"  Error: {e}\n")

    # Example 6: Graceful fallback
    try:
        example_6_graceful_fallback()
    except Exception as e:
        print(f"  Error: {e}\n")

    print("=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
