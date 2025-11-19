"""
Example 2: Error Handling - Handling Different Error Cases

This example demonstrates how to handle errors that can occur when using
the mPOHODA driver. Each error type has specific recovery strategies.

Errors covered:
- AuthenticationError - Invalid credentials
- ConnectionError - Network/API down
- ObjectNotFoundError - Object doesn't exist
- ValidationError - Invalid parameters
- RateLimitError - Too many requests

Run with:
    export MPOHODA_API_KEY=your_api_key
    python examples/error_handling.py
"""

from mpohoda import (
    MPohodaDriver,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    ValidationError,
    RateLimitError,
    TimeoutError,
)


def example_authentication_error():
    """Handle authentication errors (invalid credentials)."""
    print("\n=== Authentication Error Handling ===")

    try:
        # This will fail if credentials are invalid
        driver = MPohodaDriver(api_key="invalid_key_12345")
        driver.read("Activities")

    except AuthenticationError as e:
        print(f"❌ Authentication failed!")
        print(f"Message: {e.message}")
        print(f"Details: {e.details}")
        print("\nRecovery steps:")
        print("  1. Check your API key is correct")
        print("  2. Verify API key hasn't expired")
        print("  3. Generate a new API key if needed")
        print("  4. Set environment variable: export MPOHODA_API_KEY=your_key")


def example_object_not_found():
    """Handle when object doesn't exist."""
    print("\n=== Object Not Found Error Handling ===")

    try:
        driver = MPohodaDriver.from_env()
        try:
            # This object doesn't exist
            driver.read("NonexistentObject")
        finally:
            driver.close()

    except ObjectNotFoundError as e:
        print(f"❌ Object not found!")
        print(f"Message: {e.message}")

        # Display available objects
        if "available" in e.details:
            available = e.details["available"]
            print(f"\nAvailable objects ({len(available)}):")
            for obj in available:
                print(f"  - {obj}")

        # Display suggestions if available
        if "suggestions" in e.details:
            print(f"\nDid you mean one of these?")
            for suggestion in e.details["suggestions"]:
                print(f"  - {suggestion}")


def example_validation_error():
    """Handle validation errors (invalid parameters)."""
    print("\n=== Validation Error Handling ===")

    try:
        driver = MPohodaDriver.from_env()
        try:
            # This will fail - page_size exceeds maximum of 50
            driver.read("Activities", page_size=100)
        finally:
            driver.close()

    except ValidationError as e:
        print(f"❌ Validation error!")
        print(f"Message: {e.message}")

        # Show details for this validation error
        if "parameter" in e.details:
            param = e.details["parameter"]
            provided = e.details.get("provided")
            maximum = e.details.get("maximum")
            print(f"\nParameter: {param}")
            print(f"You provided: {provided}")
            print(f"Maximum allowed: {maximum}")

        # Show suggestion
        if "suggestion" in e.details:
            print(f"\n💡 Suggestion: {e.details['suggestion']}")


def example_rate_limit_error():
    """Handle rate limit errors."""
    print("\n=== Rate Limit Error Handling ===")

    try:
        # Create driver with low retry count for demo
        driver = MPohodaDriver.from_env(max_retries=1)
        try:
            # In real scenario, make many requests to hit rate limit
            for i in range(10000):
                driver.read("Activities")
        finally:
            driver.close()

    except RateLimitError as e:
        print(f"❌ Rate limit exceeded!")
        print(f"Message: {e.message}")

        # Show rate limit details
        if "retry_after" in e.details:
            retry_after = e.details["retry_after"]
            print(f"\nRetry after: {retry_after} seconds")

        if "limit" in e.details:
            limit = e.details["limit"]
            print(f"Limit: {limit} requests")

        if "limit_type" in e.details:
            limit_type = e.details["limit_type"]
            print(f"Type: {limit_type}")

        print("\nRecovery steps:")
        print("  1. Wait the specified number of seconds")
        print("  2. Reduce batch size for next request")
        print("  3. Consider spreading requests over time")
        print("  4. For monthly limits, wait until next month")


def example_timeout_error():
    """Handle timeout errors."""
    print("\n=== Timeout Error Handling ===")

    try:
        # Create driver with very short timeout
        driver = MPohodaDriver.from_env(timeout=0.001)
        try:
            # This will likely timeout with such short timeout
            driver.read("Activities")
        finally:
            driver.close()

    except TimeoutError as e:
        print(f"❌ Request timed out!")
        print(f"Message: {e.message}")

        # Show timeout details
        if "timeout" in e.details:
            timeout = e.details["timeout"]
            print(f"\nTimeout was set to: {timeout} seconds")

        print("\nRecovery steps:")
        print("  1. Try with longer timeout: MPohodaDriver.from_env(timeout=60)")
        print("  2. Reduce page_size to get fewer records")
        print("  3. Check your network connection")
        print("  4. Check if API is responding slowly")


def example_connection_error():
    """Handle connection errors."""
    print("\n=== Connection Error Handling ===")

    try:
        # Try to connect to invalid URL
        driver = MPohodaDriver(api_key="test", api_url="https://invalid.example.com")
        driver.read("Activities")

    except ConnectionError as e:
        print(f"❌ Connection failed!")
        print(f"Message: {e.message}")

        # Show connection details
        if "api_url" in e.details:
            api_url = e.details["api_url"]
            print(f"\nAPI URL: {api_url}")

        print("\nRecovery steps:")
        print("  1. Check your internet connection")
        print("  2. Verify API URL is correct")
        print("  3. Check if API is online: https://api.mpohoda.cz/doc")
        print("  4. Try pinging the server")


def example_graceful_degradation():
    """Example of graceful error handling in production."""
    print("\n=== Graceful Degradation Pattern ===")

    driver = None
    try:
        print("Connecting to mPOHODA API...")
        driver = MPohodaDriver.from_env()

        print("Reading activities...")
        activities = driver.read("Activities", page_size=50)
        print(f"✅ Success! Retrieved {len(activities)} activities")

    except AuthenticationError as e:
        print(f"❌ Failed to authenticate: {e.message}")
        print("   Please check your API credentials")
        return False

    except ConnectionError as e:
        print(f"❌ Failed to connect: {e.message}")
        print("   The API server may be down. Please try again later.")
        return False

    except ValidationError as e:
        print(f"❌ Validation error: {e.message}")
        print(f"   {e.details.get('suggestion', 'Check parameters')}")
        return False

    except RateLimitError as e:
        print(f"❌ Rate limit reached: {e.message}")
        wait_time = e.details.get("retry_after", 60)
        print(f"   Please wait {wait_time} seconds before retrying")
        return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

    finally:
        if driver:
            driver.close()

    return True


def main():
    """Run all error handling examples."""
    print("=" * 60)
    print("mPOHODA Driver Error Handling Examples")
    print("=" * 60)

    # Example 1: Authentication errors
    example_authentication_error()

    # Example 2: Object not found
    example_object_not_found()

    # Example 3: Validation errors
    example_validation_error()

    # Example 4: Rate limit errors
    example_rate_limit_error()

    # Example 5: Timeout errors
    example_timeout_error()

    # Example 6: Connection errors
    example_connection_error()

    # Example 7: Graceful degradation
    success = example_graceful_degradation()

    print("\n" + "=" * 60)
    if success:
        print("✅ Examples completed successfully!")
    else:
        print("⚠️  Some examples failed (expected for demo)")
    print("=" * 60)


if __name__ == "__main__":
    main()
