"""
Example: Error Handling - Comprehensive Exception Management

This example demonstrates:
- Handling missing objects (ObjectNotFoundError)
- Handling rate limits (RateLimitError)
- Handling authentication errors (AuthenticationError)
- Handling validation errors (ValidationError)
- Handling connection errors (ConnectionError)
- Retry strategies
- Helpful error reporting

Run:
    export FIDOO_API_KEY="your_api_key_here"
    python error_handling.py
"""

import time
from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import (
    ObjectNotFoundError,
    RateLimitError,
    AuthenticationError,
    ValidationError,
    ConnectionError,
    DriverError,
)


def main():
    """Demonstrate comprehensive error handling"""

    print("=" * 70)
    print("FIDOO8DRIVER - Error Handling Examples")
    print("=" * 70)

    # Try to initialize driver
    try:
        client = Fidoo8Driver.from_env()
    except AuthenticationError as e:
        print(f"\n❌ Authentication Error: {e.message}")
        print(f"   Required: {e.details.get('required_env_vars', [])}")
        print(f"   How to get API key: {e.details.get('how_to_get_api_key')}")
        return

    try:
        # Example 1: Handle missing object
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Handle Missing Object")
        print("=" * 70)

        try:
            print("\nAttempting to query non-existent object 'InvalidObject'...")
            results = client.read("InvalidObject")

        except ObjectNotFoundError as e:
            print(f"\n❌ {e.__class__.__name__}")
            print(f"   Message: {e.message}")
            print(f"   Available objects: {e.details['available'][:5]}...")

            # Retry with valid object
            print(f"\n✅ Retrying with valid object 'User'...")
            results = client.read("User", limit=5)
            print(f"   Success! Got {len(results)} users")

        # Example 2: Handle validation error (page size too large)
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Handle Validation Error")
        print("=" * 70)

        try:
            print("\nAttempting to query with limit=1000 (exceeds max of 100)...")
            results = client.read("User", limit=1000)

        except ValidationError as e:
            print(f"\n❌ {e.__class__.__name__}")
            print(f"   Message: {e.message}")
            print(f"   Details: {e.details}")

            # Retry with valid limit
            print(f"\n✅ Retrying with valid limit=50...")
            results = client.read("User", limit=50)
            print(f"   Success! Got {len(results)} users")

        # Example 3: Query field schema before querying
        print("\n" + "=" * 70)
        print("EXAMPLE 3: Inspect Schema Before Querying")
        print("=" * 70)

        try:
            # Get schema to understand object structure
            print("\nGetting field schema for 'Card' object...")
            fields = client.get_fields("Card")

            print(f"\nCard object has {len(fields)} fields:")
            for field_name, field_info in list(fields.items())[:3]:
                print(f"  - {field_name}: {field_info.get('type', 'unknown')}")
            print(f"  ... and {len(fields) - 3} more")

            # Now query cards
            print(f"\n✅ Querying cards...")
            cards = client.read("Card", limit=5)
            print(f"   Got {len(cards)} cards")

        except Exception as e:
            print(f"\n❌ Error: {e}")

        # Example 4: Demonstrate safe query pattern
        print("\n" + "=" * 70)
        print("EXAMPLE 4: Safe Query Pattern with Retry")
        print("=" * 70)

        print("\nQuerying using safe_read() function with retry logic...")
        results = safe_read(client, "User", limit=25)
        print(f"✅ Safe query returned {len(results)} records")

        # Example 5: Different exception types
        print("\n" + "=" * 70)
        print("EXAMPLE 5: Exception Hierarchy")
        print("=" * 70)

        print("\nException types handled by Fidoo8Driver:")
        exception_types = [
            ("ObjectNotFoundError", "Invalid object name"),
            ("ValidationError", "Invalid parameters (e.g., limit > 100)"),
            ("RateLimitError", "API rate limit exceeded (HTTP 429)"),
            ("AuthenticationError", "Invalid credentials (HTTP 401/403)"),
            ("ConnectionError", "Network error or API down (HTTP 5xx)"),
            ("TimeoutError", "Request timeout"),
            ("QuerySyntaxError", "Invalid query syntax"),
        ]

        for exc_type, description in exception_types:
            print(f"  • {exc_type:<30} - {description}")

        print("\n" + "=" * 70)
        print("✅ Error handling examples completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.close()


def safe_read(client, object_name, limit=50, max_attempts=3):
    """
    Query with automatic retry on errors.

    Args:
        client: Fidoo8Driver instance
        object_name: Object to query
        limit: Records per request
        max_attempts: Maximum retry attempts

    Returns:
        List of records or empty list on permanent failure
    """
    for attempt in range(1, max_attempts + 1):
        try:
            if attempt > 1:
                print(f"  Attempt {attempt}/{max_attempts}...", end=" ")

            results = client.read(object_name, limit=limit)

            if attempt > 1:
                print("✅ Success!")

            return results

        except RateLimitError as e:
            retry_after = e.details.get("retry_after", 60)
            if attempt < max_attempts:
                print(f"Rate limited! Waiting {retry_after}s...")
                time.sleep(retry_after)
            else:
                print(f"Rate limited (max attempts reached)")
                raise

        except (ValidationError, ObjectNotFoundError) as e:
            # Permanent errors - don't retry
            print(f"Permanent error: {e.message}")
            raise

        except ConnectionError as e:
            # Transient errors - retry with backoff
            if attempt < max_attempts:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Connection error! Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Connection error (max attempts reached)")
                raise

    return []


if __name__ == "__main__":
    main()
