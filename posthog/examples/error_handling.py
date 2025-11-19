#!/usr/bin/env python3
"""
Error Handling Example

Demonstrates proper error handling and recovery:
- Authentication errors
- Connection errors
- Resource not found errors
- Validation errors
- Rate limit errors
- Graceful error recovery

This example shows how to properly handle errors that may occur
when using the PostHog driver.

Requirements:
    - POSTHOG_API_KEY environment variable set

Usage:
    python error_handling.py
"""

from posthog_driver import (
    PostHogDriver,
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    FieldNotFoundError,
    ValidationError,
    RateLimitError,
    DriverError,
)


def demonstrate_authentication_error():
    """Show how to handle authentication errors."""
    print("\n" + "=" * 70)
    print("1. Demonstrating Authentication Error Handling")
    print("=" * 70)

    try:
        # Try to initialize with invalid credentials
        driver = PostHogDriver(
            api_url="https://app.posthog.com/api",
            api_key="invalid_key_for_demo"
        )
        print("✓ Driver initialized (skipped auth validation in this demo)")
        driver.close()

    except AuthenticationError as e:
        print(f"✗ Authentication Error Caught!")
        print(f"  Message: {e.message}")
        print(f"  Suggestion: {e.details.get('suggestion')}")
        print(f"  Required vars: {e.details.get('required_env_vars')}")


def demonstrate_validation_error():
    """Show how to handle validation errors."""
    print("\n" + "=" * 70)
    print("2. Demonstrating Validation Error Handling")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Try to read with invalid page size
        results = driver.read("/dashboards", limit=101)  # Exceeds max of 100

    except ValidationError as e:
        print(f"✓ Validation Error Caught!")
        print(f"  Message: {e.message}")
        print(f"  Provided: {e.details.get('provided')}")
        print(f"  Maximum: {e.details.get('maximum')}")
        print(f"  Suggestion: {e.details.get('suggestion')}")

        # Recover by using valid page size
        print(f"\n  Recovering with valid page size (50)...")
        try:
            results = driver.read("/dashboards", limit=50)
            print(f"  ✓ Successfully read {len(results)} dashboards")
        except Exception as e:
            print(f"  ✗ Recovery failed: {e}")

    finally:
        driver.close()


def demonstrate_object_not_found_error():
    """Show how to handle object not found errors."""
    print("\n" + "=" * 70)
    print("3. Demonstrating Object Not Found Error Handling")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Try to get schema for non-existent object
        fields = driver.get_fields("nonexistent_object")

    except ObjectNotFoundError as e:
        print(f"✓ Object Not Found Error Caught!")
        print(f"  Message: {e.message}")
        print(f"  Requested: {e.details.get('requested')}")
        print(f"  Available: {e.details.get('available')}")

        # Recover by listing available objects
        print(f"\n  Recovering by showing available resources...")
        try:
            available = driver.list_objects()
            print(f"  ✓ Available resources:")
            for obj in available[:5]:
                print(f"    - {obj}")
            if len(available) > 5:
                print(f"    ... and {len(available) - 5} more")
        except Exception as e:
            print(f"  ✗ Recovery failed: {e}")

    finally:
        driver.close()


def demonstrate_batch_operation_with_error_handling():
    """Show how to handle errors during batch operations."""
    print("\n" + "=" * 70)
    print("4. Demonstrating Error Handling in Batch Operations")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Process data in batches with error handling
        total_processed = 0
        batches_processed = 0

        print("  Processing events in batches...")

        for batch in driver.read_batched("/events", batch_size=100):
            try:
                batches_processed += 1
                total_processed += len(batch)

                # Simulate processing each batch
                print(f"  ✓ Processed batch {batches_processed}: {len(batch)} events")

                # Only process first 3 batches in this demo
                if batches_processed >= 3:
                    print(f"  (Stopping after 3 batches for demo purposes)")
                    break

            except Exception as e:
                print(f"  ✗ Error processing batch {batches_processed}: {e}")
                # Continue with next batch instead of crashing

        print(f"\n  Total processed: {total_processed} events in {batches_processed} batches")

    except RateLimitError as e:
        print(f"✓ Rate Limit Error Caught!")
        print(f"  Message: {e.message}")
        retry_after = e.details.get('retry_after', 60)
        print(f"  Retry after: {retry_after} seconds")
        print(f"  Suggestion: {e.details.get('suggestion')}")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    finally:
        driver.close()


def demonstrate_generic_error_handling():
    """Show how to handle any driver error generically."""
    print("\n" + "=" * 70)
    print("5. Demonstrating Generic Error Handling")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # This operation should succeed
        objects = driver.list_objects()
        print(f"✓ Successfully listed {len(objects)} resource types")

    except DriverError as e:
        # Catch any driver error
        print(f"✗ Driver Error: {e}")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Details: {e.details}")

    except Exception as e:
        # Catch unexpected errors
        print(f"✗ Unexpected Error: {e}")

    finally:
        driver.close()


def demonstrate_context_manager_pattern():
    """Show best practice using context manager pattern."""
    print("\n" + "=" * 70)
    print("6. Demonstrating Context Manager Pattern (Best Practice)")
    print("=" * 70)

    try:
        # Recommended: Always use try/finally pattern
        driver = PostHogDriver.from_env()

        try:
            dashboards = driver.read("/dashboards", limit=5)
            print(f"✓ Successfully read {len(dashboards)} dashboards")
            print("  This code is guaranteed to cleanup resources")

        except DriverError as e:
            print(f"✗ Error during operation: {e.message}")
            print(f"  Suggestion: {e.details.get('suggestion')}")

        finally:
            driver.close()
            print("  Resources cleaned up")

    except Exception as e:
        print(f"✗ Failed to initialize driver: {e}")


def main():
    """Run all error handling demonstrations."""
    print("=" * 70)
    print("PostHog Driver - Error Handling Examples")
    print("=" * 70)

    try:
        # Run demonstrations in order
        demonstrate_authentication_error()
        demonstrate_validation_error()
        demonstrate_object_not_found_error()
        demonstrate_batch_operation_with_error_handling()
        demonstrate_generic_error_handling()
        demonstrate_context_manager_pattern()

    except KeyboardInterrupt:
        print("\n\nExample interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error in main: {e}")

    print("\n" + "=" * 70)
    print("All error handling examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
