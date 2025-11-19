"""
Example 2: Error Handling

Demonstrates exception handling patterns:
- Catching specific exceptions
- Accessing error details
- Recovery strategies
- Structured error information

This example shows how to handle different error scenarios
that may occur when using the Stripe driver.
"""

from stripe_driver import (
    StripeDriver,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    ValidationError,
    RateLimitError,
    TimeoutError,
)


def handle_auth_error():
    """Demonstrate authentication error handling."""
    print("\n[Test 1] Authentication Error Handling")
    print("-" * 70)

    try:
        print("  Attempting to initialize with invalid API key...")
        client = StripeDriver(api_key="invalid_key_12345")
    except AuthenticationError as e:
        print(f"  ✓ Caught AuthenticationError")
        print(f"    Message: {e.message}")
        print(f"    Details: {e.details}")
        print(f"    Action: Check STRIPE_API_KEY environment variable")


def handle_validation_error():
    """Demonstrate validation error handling."""
    print("\n[Test 2] Validation Error Handling")
    print("-" * 70)

    try:
        client = StripeDriver.from_env()
        print("  Attempting to query with invalid page size (limit=500)...")
        # Stripe max limit is 100
        products = client.read("products", limit=500)
    except ValidationError as e:
        print(f"  ✓ Caught ValidationError")
        print(f"    Message: {e.message}")
        print(f"    Details: {e.details}")

        # Extract details for structured handling
        if "maximum" in e.details:
            max_limit = e.details["maximum"]
            print(f"    Action: Use limit <= {max_limit}")

        client.close()
    except Exception as e:
        print(f"  Unexpected error: {e}")


def handle_object_not_found():
    """Demonstrate object not found handling."""
    print("\n[Test 3] Object Not Found Handling")
    print("-" * 70)

    try:
        client = StripeDriver.from_env()
        print("  Attempting to query non-existent resource 'invalid_resource'...")
        # This resource doesn't exist in Stripe
        results = client.read("invalid_resource", limit=10)
    except ObjectNotFoundError as e:
        print(f"  ✓ Caught ObjectNotFoundError")
        print(f"    Message: {e.message}")
        print(f"    Details: {e.details}")

        # Use suggestions to help user
        if "available" in e.details:
            available = e.details["available"]
            print(f"    Available resources: {available[:5]}...")

        client.close()
    except Exception as e:
        print(f"  Unexpected error: {e}")


def handle_connection_error():
    """Demonstrate connection error handling."""
    print("\n[Test 4] Connection Error Handling (Simulated)")
    print("-" * 70)

    try:
        print("  Attempting to connect to invalid API URL...")
        client = StripeDriver(api_key="sk_test_123", base_url="https://invalid.example.com")
    except ConnectionError as e:
        print(f"  ✓ Caught ConnectionError")
        print(f"    Message: {e.message}")
        print(f"    Details: {e.details}")
        print(f"    Action: Check API URL and internet connection")
    except Exception as e:
        print(f"  Note: {type(e).__name__}: {e}")


def error_handling_best_practices():
    """Demonstrate error handling best practices."""
    print("\n[Test 5] Error Handling Best Practices")
    print("-" * 70)

    client = None
    try:
        client = StripeDriver.from_env()

        # Best practice 1: Specific exception handling
        print("  Best Practice 1: Catch specific exceptions")
        try:
            products = client.read("products", limit=10)
            print(f"    ✓ Successfully read {len(products)} products")
        except ValidationError as e:
            print(f"    ✗ Validation error: {e.message}")
        except ConnectionError as e:
            print(f"    ✗ Connection error: {e.message}")

        # Best practice 2: Access structured details
        print("\n  Best Practice 2: Use structured error details")
        try:
            products = client.read("products", limit=150)
        except ValidationError as e:
            if "maximum" in e.details:
                # Retry with valid limit
                max_limit = e.details["maximum"]
                print(f"    ✓ Detected max limit: {max_limit}")
                products = client.read("products", limit=max_limit)
                print(f"    ✓ Successfully retried with limit={max_limit}")

        # Best practice 3: Rate limit recovery
        print("\n  Best Practice 3: Rate limit recovery")
        try:
            # Simulate multiple requests
            for i in range(3):
                products = client.read("products", limit=10)
                print(f"    ✓ Request {i+1} succeeded")
        except RateLimitError as e:
            retry_after = e.details.get("retry_after", 60)
            print(f"    ✗ Rate limited")
            print(f"    ✓ Retry after {retry_after} seconds")
            import time
            # In real code: time.sleep(retry_after)

        # Best practice 4: Timeout handling
        print("\n  Best Practice 4: Timeout handling")
        try:
            client_with_timeout = StripeDriver.from_env(timeout=5)
            products = client_with_timeout.read("products", limit=10)
            print(f"    ✓ Request completed within timeout")
            client_with_timeout.close()
        except TimeoutError as e:
            print(f"    ✗ Request timeout: {e.message}")

    except Exception as e:
        print(f"  Unexpected error: {type(e).__name__}: {e}")

    finally:
        # Best practice 5: Always cleanup
        if client:
            client.close()
            print("\n  Best Practice 5: Always cleanup resources")
            print("    ✓ Client closed")


def main():
    """Run all error handling examples."""
    print("=" * 70)
    print("Example 2: Error Handling")
    print("=" * 70)

    # Test authentication error
    handle_auth_error()

    # Test validation error
    handle_validation_error()

    # Test object not found
    handle_object_not_found()

    # Test connection error
    handle_connection_error()

    # Best practices
    error_handling_best_practices()

    print("\n" + "=" * 70)
    print("✓ Error handling examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
