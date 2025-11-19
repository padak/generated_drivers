#!/usr/bin/env python3
"""
Example: Error handling patterns

This example demonstrates comprehensive error handling for different failure scenarios.

Usage:
    export FIDOO_API_KEY="your_api_key_here"
    python error_handling.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fidoo7 import (
    Fidoo7Driver,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    RateLimitError,
    ValidationError,
    TimeoutError,
)


def example_invalid_credentials():
    """Example: Handling authentication errors"""
    print("\n1. Authentication Error Example")
    print("-" * 60)

    try:
        # This will fail with AuthenticationError
        client = Fidoo7Driver(api_key="invalid_key_12345")
    except AuthenticationError as e:
        print(f"✗ {e}")
        print(f"  Details: {e.details}")
        print(f"  Action: Check your FIDOO_API_KEY environment variable")


def example_invalid_endpoint():
    """Example: Handling invalid endpoint"""
    print("\n2. Object Not Found Example")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # This will fail with ObjectNotFoundError
        results = client.read("invalid/endpoint")
    except ObjectNotFoundError as e:
        print(f"✗ {e}")
        print(f"  Available endpoints: {client.list_objects()}")
        print(f"  Action: Use one of the available endpoints above")
    finally:
        client.close()


def example_validation_error():
    """Example: Handling validation errors"""
    print("\n3. Validation Error Example")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Invalid page size (exceeds max of 100)
        results = client.read("user/get-users", limit=500)
    except ValidationError as e:
        print(f"✗ {e}")
        print(f"  Details: {e.details}")
        print(f"  Action: Use limit <= {e.details['maximum']}")
    finally:
        client.close()


def example_field_discovery():
    """Example: Safe field access"""
    print("\n4. Safe Field Access Example")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Get field schema to discover available fields
        fields = client.get_fields("user")
        print(f"Available user fields: {list(fields.keys())}")

        # Now safely read and display data
        users = client.read("user/get-users", limit=5)
        if users:
            user = users[0]
            # Safely access fields with .get()
            print(f"First user: {user.get('firstName', 'N/A')} {user.get('lastName', 'N/A')}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()


def example_rate_limiting():
    """Example: Handling rate limits"""
    print("\n5. Rate Limiting Example")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Check rate limit status
        status = client.get_rate_limit_status()
        print(f"Rate limit: {status['limit']} requests per day")

        # Make requests (normally)
        users = client.read("user/get-users", limit=10)
        print(f"Fetched {len(users)} users")

        # If you encounter rate limit:
        # The driver automatically retries with exponential backoff
        # But you can catch RateLimitError if retries exhausted
    except RateLimitError as e:
        print(f"✗ {e}")
        print(f"  Retry after: {e.details['retry_after']} seconds")
        print(f"  Action: Wait before retrying or reduce batch size")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()


def example_connection_error():
    """Example: Handling connection errors"""
    print("\n6. Connection Error Example")
    print("-" * 60)

    try:
        # Try to connect with invalid URL
        client = Fidoo7Driver(
            base_url="https://invalid.example.com/v2/",
            api_key="test_key"
        )
    except ConnectionError as e:
        print(f"✗ {e}")
        print(f"  Details: {e.details}")
        print(f"  Action: Check API URL and network connectivity")


def example_comprehensive_error_handling():
    """Example: Comprehensive error handling in real code"""
    print("\n7. Comprehensive Error Handling Pattern")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        print("Reading users from Fidoo...")

        users = client.read("user/get-users", limit=50)
        print(f"✓ Successfully fetched {len(users)} users")

        # Process users safely
        for user in users:
            first_name = user.get("firstName", "Unknown")
            email = user.get("email", "N/A")
            print(f"  • {first_name} ({email})")

    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e.message}")
        print("  → Check your API credentials")
        return 1

    except RateLimitError as e:
        print(f"✗ Rate limit exceeded: {e.message}")
        print(f"  → Wait {e.details['retry_after']} seconds and retry")
        return 1

    except ObjectNotFoundError as e:
        print(f"✗ Endpoint not found: {e.message}")
        available = client.list_objects()
        print(f"  → Available endpoints: {', '.join(available[:5])}...")
        return 1

    except TimeoutError as e:
        print(f"✗ Request timeout: {e.message}")
        print("  → Try increasing timeout or reducing batch size")
        return 1

    except ConnectionError as e:
        print(f"✗ Connection failed: {e.message}")
        print("  → Check network connectivity and API URL")
        return 1

    except ValidationError as e:
        print(f"✗ Validation error: {e.message}")
        print(f"  → Details: {e.details}")
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 1

    finally:
        client.close()

    return 0


def main():
    print("=" * 60)
    print("Fidoo7 Driver - Error Handling Examples")
    print("=" * 60)

    # Run examples
    example_invalid_credentials()
    example_invalid_endpoint()
    example_validation_error()
    example_field_discovery()
    example_rate_limiting()
    example_connection_error()
    return example_comprehensive_error_handling()


if __name__ == "__main__":
    sys.exit(main())
