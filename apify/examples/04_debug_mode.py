"""
Example 4: Debug Mode & Troubleshooting

Demonstrates debugging and troubleshooting techniques:
- Enable debug logging to see all API calls
- Inspect rate limit status
- Monitor API responses
- Troubleshoot authentication issues
- Check driver capabilities

Prerequisites:
    export APIFY_API_TOKEN="your_token_here"

Run:
    python examples/04_debug_mode.py
"""

import logging
from apify_driver import ApifyDriver, AuthenticationError


def setup_logging():
    """Configure logging for visibility"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def example_debug_logging():
    """Example: Enable debug logging to see API calls"""
    print("\n1. DEBUG LOGGING")
    print("-" * 70)

    print("Creating client with debug=True...")
    client = ApifyDriver.from_env(debug=True)

    try:
        print("Making API call (watch for [DEBUG] messages)...")
        actors = client.read("/actors", limit=2)
        print(f"✓ Retrieved {len(actors)} actors")

    finally:
        client.close()


def example_driver_info():
    """Example: Inspect driver configuration"""
    print("\n2. DRIVER CONFIGURATION")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print(f"API URL: {client.api_url}")
        print(f"Timeout: {client.timeout} seconds")
        print(f"Max retries: {client.max_retries}")
        print(f"Debug mode: {client.debug}")

    finally:
        client.close()


def example_capabilities():
    """Example: Check driver capabilities"""
    print("\n3. DRIVER CAPABILITIES")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        capabilities = client.get_capabilities()

        print("Operation Support:")
        print(f"  Read: {capabilities.read}")
        print(f"  Write: {capabilities.write}")
        print(f"  Update: {capabilities.update}")
        print(f"  Delete: {capabilities.delete}")

        print("\nFeature Support:")
        print(f"  Batch operations: {capabilities.batch_operations}")
        print(f"  Streaming: {capabilities.streaming}")
        print(f"  Transactions: {capabilities.supports_transactions}")
        print(f"  Relationships: {capabilities.supports_relationships}")

        print("\nPagination:")
        print(f"  Style: {capabilities.pagination.value}")
        print(f"  Max page size: {capabilities.max_page_size}")

        if capabilities.query_language:
            print(f"  Query language: {capabilities.query_language}")
        else:
            print("  Query language: None (REST API)")

    finally:
        client.close()


def example_rate_limit_status():
    """Example: Check rate limit status"""
    print("\n4. RATE LIMIT STATUS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Make a request first
        print("Making API call...")
        actors = client.read("/actors", limit=1)

        # Check rate limit status
        print("\nRate limit status:")
        status = client.get_rate_limit_status()

        print(f"  Remaining requests: {status.get('remaining', 'N/A')}")
        print(f"  Rate limit: {status.get('limit', 'N/A')}")
        print(f"  Reset at: {status.get('reset_at', 'N/A')}")
        print(f"  Retry after: {status.get('retry_after', 'N/A')} seconds")

    finally:
        client.close()


def example_resource_discovery():
    """Example: Discover available resources and fields"""
    print("\n5. RESOURCE DISCOVERY")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # List all resources
        print("Available resources:")
        resources = client.list_objects()
        for resource in resources:
            print(f"  • {resource}")

        # Get schema for one resource
        print("\nActor schema:")
        fields = client.get_fields("actors")
        print(f"  Total fields: {len(fields)}")
        print("  First 5 fields:")
        for field_name, field_info in list(fields.items())[:5]:
            field_type = field_info.get('type', 'unknown')
            description = field_info.get('description', '')
            print(f"    • {field_name} ({field_type})")
            if description:
                print(f"      {description}")

    finally:
        client.close()


def example_error_investigation():
    """Example: Investigate errors"""
    print("\n6. ERROR INVESTIGATION")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Attempting invalid query to inspect error...")

        try:
            # Try to read with invalid page size
            results = client.read("/actors", limit=500)

        except Exception as e:
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e.message if hasattr(e, 'message') else str(e)}")
            print(f"Error details: {e.details if hasattr(e, 'details') else 'N/A'}")

    finally:
        client.close()


def example_timeout_configuration():
    """Example: Configure timeout for different scenarios"""
    print("\n7. TIMEOUT CONFIGURATION")
    print("-" * 70)

    scenarios = [
        (5, "Fast API response (5s)"),
        (30, "Default (30s) - most use cases"),
        (60, "Slow API or large responses (60s)"),
        (120, "Very large dataset processing (120s)"),
    ]

    print("Timeout scenarios:")
    for timeout, description in scenarios:
        print(f"  • {description}")
        print(f"    client = ApifyDriver.from_env(timeout={timeout})")

    # Demo with default
    print(f"\nCurrent configuration uses default timeout")
    client = ApifyDriver.from_env()
    print(f"  Timeout: {client.timeout} seconds")
    client.close()


def example_retry_configuration():
    """Example: Configure retry strategy"""
    print("\n8. RETRY CONFIGURATION")
    print("-" * 70)

    scenarios = [
        (0, "No retry (fail fast)"),
        (1, "Single retry (3 total attempts)"),
        (3, "Default - 3 retries (4 total attempts)"),
        (5, "High availability - 5 retries (6 total attempts)"),
    ]

    print("Retry scenarios:")
    for retries, description in scenarios:
        print(f"  • {description}")
        print(f"    client = ApifyDriver.from_env(max_retries={retries})")
        print(f"    Backoff: exponential (1s, 2s, 4s, 8s, ...)")

    print("\nRetry behavior:")
    print("  1. HTTP 429 (rate limit) triggers retry")
    print("  2. Wait increases: 2^attempt seconds")
    print("  3. Max attempts: 1 + max_retries")
    print("  4. Other errors: no retry (fail immediately)")


def example_environment_check():
    """Example: Check environment setup"""
    print("\n9. ENVIRONMENT CHECK")
    print("-" * 70)

    import os

    print("Required environment variables:")
    api_token = os.getenv("APIFY_API_TOKEN")
    print(f"  APIFY_API_TOKEN: {'✓ Set' if api_token else '✗ Not set'}")

    print("\nOptional environment variables:")
    api_url = os.getenv("APIFY_API_URL")
    print(f"  APIFY_API_URL: {'✓ Set' if api_url else '✗ Not set (using default)'}")

    if not api_token:
        print("\n⚠️  Missing APIFY_API_TOKEN")
        print("   Set it with: export APIFY_API_TOKEN=\"your_token\"")
        print("   Get token from: https://console.apify.com/settings/integrations")


def example_health_check():
    """Example: Verify API connectivity"""
    print("\n10. HEALTH CHECK")
    print("-" * 70)

    try:
        print("Checking API connectivity...")
        client = ApifyDriver.from_env()

        # Try a simple read
        actors = client.read("/actors", limit=1)
        print("✓ API is reachable")
        print(f"✓ Authentication successful")
        print(f"✓ Retrieved {len(actors)} actor(s)")

        client.close()

    except AuthenticationError as e:
        print(f"❌ Authentication failed")
        print(f"   Message: {e.message}")
        print(f"   Solution: Check APIFY_API_TOKEN")

    except Exception as e:
        print(f"❌ Connection failed")
        print(f"   Error: {type(e).__name__}: {e}")
        print(f"   Solution: Check API URL and network")


def main():
    """Run all debugging and troubleshooting examples"""
    print("=" * 70)
    print("EXAMPLE 4: Debug Mode & Troubleshooting")
    print("=" * 70)

    example_driver_info()
    example_capabilities()
    example_rate_limit_status()
    example_resource_discovery()
    example_error_investigation()
    example_timeout_configuration()
    example_retry_configuration()
    example_environment_check()
    example_health_check()
    example_debug_logging()

    print("\n" + "=" * 70)
    print("✓ Debug and troubleshooting examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
