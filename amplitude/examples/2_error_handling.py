#!/usr/bin/env python3
"""
Example 2: Error Handling

Demonstrates exception handling patterns:
- AuthenticationError - Invalid credentials
- ValidationError - Invalid data
- RateLimitError - Rate limit exceeded
- ConnectionError - Cannot reach API
- TimeoutError - Request timeout

Run this example:
    export AMPLITUDE_API_KEY="your_api_key"
    python 2_error_handling.py
"""

from amplitude import AmplitudeDriver
from amplitude.exceptions import (
    AuthenticationError,
    ConnectionError,
    ValidationError,
    RateLimitError,
    TimeoutError,
    DriverError,
)


def example_authentication_error():
    """Example: Handle authentication errors."""
    print("\n" + "=" * 70)
    print("Example: Authentication Error")
    print("=" * 70)

    try:
        # This will raise AuthenticationError if API key is not set
        driver = AmplitudeDriver.from_env()
        print("✓ Driver initialized successfully")
    except AuthenticationError as e:
        print(f"✗ Authentication error: {e.message}")
        print(f"  Suggestion: {e.details.get('suggestion')}")
        print(f"  Required env vars: {e.details.get('required_env_vars')}")


def example_validation_error():
    """Example: Handle validation errors (invalid event data)."""
    print("\n" + "=" * 70)
    print("Example: Validation Error (Batch Too Large)")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Create a batch that exceeds the limit (max 2000 events)
        huge_batch = [
            {
                "user_id": f"user_{i}",
                "event_type": "test_event",
            }
            for i in range(2500)  # Exceeds 2000 limit
        ]

        print(f"Attempting to upload {len(huge_batch)} events...")
        result = driver.create_batch(huge_batch)

    except ValidationError as e:
        print(f"✗ Validation error: {e.message}")
        print(f"  Provided: {e.details.get('provided')}")
        print(f"  Maximum: {e.details.get('maximum')}")
        print(f"  Suggestion: {e.details.get('suggestion')}")

    finally:
        driver.close()


def example_validation_error_missing_field():
    """Example: Handle validation errors (missing required field)."""
    print("\n" + "=" * 70)
    print("Example: Validation Error (Missing Required Field)")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Invalid event: missing both user_id and device_id
        invalid_event = {
            "event_type": "test_event",
            # Missing user_id and device_id (at least one required)
        }

        print("Attempting to upload invalid event...")
        result = driver.create("events", invalid_event)

    except ValidationError as e:
        print(f"✗ Validation error: {e.message}")
        print(f"  Missing fields: {e.details.get('missing_fields')}")
        print(f"  Note: {e.details.get('note')}")

    finally:
        driver.close()


def example_rate_limit_handling():
    """Example: Handle rate limit errors."""
    print("\n" + "=" * 70)
    print("Example: Rate Limit Error (Automatic Retry)")
    print("=" * 70)

    print("Note: This example shows how rate limits are handled automatically.")
    print("      The driver will retry up to max_retries times with exponential backoff.")
    print("      This example won't actually trigger a rate limit unless you send")
    print("      many requests quickly.")

    try:
        # Configure driver with debug logging to see retries
        driver = AmplitudeDriver.from_env(debug=True, max_retries=3)
        print("✓ Driver initialized with debug logging and 3 retries")

        events = [
            {
                "user_id": "user_test",
                "event_type": "test_event",
            }
        ]

        result = driver.create_batch(events)
        print(f"✓ Batch uploaded: {result.get('events_ingested')} events ingested")

    except RateLimitError as e:
        print(f"✗ Rate limit error (after retries): {e.message}")
        print(f"  Retry after: {e.details.get('retry_after')} seconds")
        print(f"  Attempts: {e.details.get('attempts')}")

    finally:
        driver.close()


def example_timeout_error():
    """Example: Handle timeout errors."""
    print("\n" + "=" * 70)
    print("Example: Timeout Error")
    print("=" * 70)

    print("Note: This example demonstrates timeout configuration.")
    print("      To trigger a timeout, set a very short timeout value.")

    try:
        # Very short timeout to demonstrate error handling
        driver = AmplitudeDriver.from_env(timeout=0.001)
        print("✓ Driver initialized with 1ms timeout (very short)")

        # This will likely timeout
        events = [
            {
                "user_id": "user_test",
                "event_type": "test_event",
            }
        ]

        print("Attempting batch upload with short timeout...")
        result = driver.create_batch(events)

    except TimeoutError as e:
        print(f"✗ Timeout error: {e.message}")
        print(f"  Timeout duration: {e.details.get('timeout')} seconds")
        print(f"  Suggestion: {e.details.get('suggestion')}")

    except Exception as e:
        # Might get connection errors too
        print(f"✗ Error: {type(e).__name__}: {e}")

    finally:
        driver.close()


def example_error_structure():
    """Example: Understanding error structure."""
    print("\n" + "=" * 70)
    print("Example: Error Structure")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Try to get schema for non-existent object
        fields = driver.get_fields("non_existent_object")

    except DriverError as e:
        print(f"Exception type: {type(e).__name__}")
        print(f"Message: {e.message}")
        print(f"Details (structured data):")
        for key, value in e.details.items():
            print(f"  {key}: {value}")

    finally:
        driver.close()


def main():
    """Run all error handling examples."""
    print("=" * 70)
    print("Amplitude Driver - Error Handling Examples")
    print("=" * 70)

    # Run examples
    example_authentication_error()
    example_validation_error()
    example_validation_error_missing_field()
    example_rate_limit_handling()
    example_timeout_error()
    example_error_structure()

    print("\n" + "=" * 70)
    print("Error handling examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
