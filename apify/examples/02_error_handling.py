"""
Example 2: Error Handling

Demonstrates comprehensive error handling with ApifyDriver:
- Authentication errors
- Connection errors
- Resource not found errors
- Query syntax errors
- Rate limit errors
- Validation errors
- Timeout errors

This example intentionally triggers various error conditions
to show how to handle them gracefully.

Prerequisites:
    export APIFY_API_TOKEN="your_token_here"

Run:
    python examples/02_error_handling.py
"""

from apify_driver import (
    ApifyDriver,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    FieldNotFoundError,
    QuerySyntaxError,
    RateLimitError,
    ValidationError,
    TimeoutError as DriverTimeoutError,
)


def handle_authentication_errors():
    """Example: Handle authentication errors"""
    print("\n1. AUTHENTICATION ERRORS")
    print("-" * 70)

    # Missing API token will raise AuthenticationError
    try:
        # This would fail if APIFY_API_TOKEN is not set
        client = ApifyDriver.from_env()
        print("✓ Authentication successful")
        client.close()

    except AuthenticationError as e:
        print(f"❌ Authentication error: {e.message}")
        print(f"   Details: {e.details}")
        print("   Solution: Set APIFY_API_TOKEN environment variable")


def handle_object_not_found():
    """Example: Handle object/resource not found"""
    print("\n2. OBJECT NOT FOUND")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Try to query a non-existent resource
        print("Attempting to read from /invalid-endpoint...")
        results = client.read("/invalid-endpoint")

    except ObjectNotFoundError as e:
        print(f"❌ Resource not found: {e.message}")
        print(f"   Endpoint: {e.details.get('endpoint', 'N/A')}")
        print("   Solution: Use client.list_objects() to see available resources")

        # Show how to discover available resources
        print("\n   Available resources:")
        resources = client.list_objects()
        for resource in resources:
            print(f"     • {resource}")

    finally:
        client.close()


def handle_validation_errors():
    """Example: Handle validation errors"""
    print("\n3. VALIDATION ERRORS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Page size exceeds maximum (100)
        print("Attempting to read with page_size=500 (exceeds max of 100)...")
        results = client.read("/actors", limit=500)

    except ValidationError as e:
        print(f"❌ Validation error: {e.message}")
        print(f"   Details: {e.details}")
        print("   Solution: Use limit <= 100")

    finally:
        client.close()


def handle_rate_limit_errors():
    """Example: Handle rate limit errors"""
    print("\n4. RATE LIMIT ERRORS")
    print("-" * 70)

    client = ApifyDriver.from_env(max_retries=1)  # Set to 1 for demo

    try:
        # Note: Triggering real rate limit errors requires many requests
        # This example shows the error structure
        print("Rate limit handling is automatic with exponential backoff")
        print(f"Default max_retries: 3 (configurable)")
        print("Each retry waits longer: 1s, 2s, 4s, 8s, etc.")

        # If you want to simulate, you could make many rapid requests:
        print("\nMaking multiple requests to demonstrate retry behavior...")
        for i in range(3):
            results = client.read("/actors", limit=1)
            print(f"  Request {i+1}: Success")

    except RateLimitError as e:
        print(f"❌ Rate limit exceeded: {e.message}")
        print(f"   Retry after: {e.details.get('retry_after', 'N/A')} seconds")
        print(f"   Solution: Wait and retry later, or use batch processing")

    finally:
        client.close()


def handle_field_errors():
    """Example: Handle field not found errors"""
    print("\n5. FIELD ERRORS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Get valid fields for actors
        fields = client.get_fields("actors")
        print(f"✓ Actor has {len(fields)} fields:")
        for field in list(fields.keys())[:5]:
            print(f"  • {field}")

    except FieldNotFoundError as e:
        print(f"❌ Field error: {e.message}")
        print(f"   Details: {e.details}")

    finally:
        client.close()


def handle_connection_errors():
    """Example: Handle connection errors"""
    print("\n6. CONNECTION ERRORS")
    print("-" * 70)

    try:
        # Try to connect to invalid URL
        print("Attempting connection to invalid API URL...")
        client = ApifyDriver(
            api_url="https://invalid-api-url-that-does-not-exist.com",
            api_key="test_token"
        )

    except ConnectionError as e:
        print(f"❌ Connection error: {e.message}")
        print(f"   Details: {e.details}")
        print("   Solution: Check API URL and network connectivity")

    except AuthenticationError:
        # May also be auth error during validation
        print("❌ Connection validation failed (auth or network)")


def handle_timeout_errors():
    """Example: Handle timeout errors"""
    print("\n7. TIMEOUT ERRORS")
    print("-" * 70)

    try:
        # Set very short timeout
        print("Using timeout=1 second (will likely timeout)...")
        client = ApifyDriver.from_env(timeout=1)
        results = client.read("/actors", limit=1000000)  # Large request

    except DriverTimeoutError as e:
        print(f"❌ Timeout error: {e.message}")
        print(f"   Details: {e.details}")
        print("   Solution: Increase timeout or reduce request size")

    except Exception as e:
        print(f"Note: Got {type(e).__name__} (timeout behavior depends on network)")

    finally:
        try:
            client.close()
        except:
            pass


def demonstrate_error_recovery():
    """Example: Demonstrate error recovery and retry"""
    print("\n8. ERROR RECOVERY & RETRY")
    print("-" * 70)

    client = ApifyDriver.from_env(max_retries=3)

    print("Attempting to read with automatic retry on rate limits...")
    print(f"Configuration: max_retries=3, backoff_factor=2")

    try:
        # Normal operation - will retry if rate limited
        results = client.read("/actors", limit=10)
        print(f"✓ Successfully retrieved {len(results)} actors")

        # For demo: Show rate limit detection
        print("\nRate limit status:")
        status = client.get_rate_limit_status()
        print(f"  Remaining requests: {status.get('remaining', 'N/A')}")
        print(f"  Rate limit: {status.get('limit', 'N/A')}")
        print(f"  Reset at: {status.get('reset_at', 'N/A')}")

    except Exception as e:
        print(f"Error after retries: {type(e).__name__}: {e}")

    finally:
        client.close()


def main():
    """Run all error handling examples"""
    print("=" * 70)
    print("EXAMPLE 2: Error Handling")
    print("=" * 70)

    handle_authentication_errors()
    handle_object_not_found()
    handle_validation_errors()
    handle_rate_limit_errors()
    handle_field_errors()
    handle_connection_errors()
    handle_timeout_errors()
    demonstrate_error_recovery()

    print("\n" + "=" * 70)
    print("✓ Error handling examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
