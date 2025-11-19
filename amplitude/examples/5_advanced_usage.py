#!/usr/bin/env python3
"""
Example 5: Advanced Usage

Demonstrates advanced patterns:
- Context manager for resource management
- Retry configuration
- Debug logging
- Concurrent operations
- Production patterns

Run this example:
    export AMPLITUDE_API_KEY="your_api_key"
    python 5_advanced_usage.py
"""

import time
from amplitude import AmplitudeDriver
from amplitude.exceptions import RateLimitError, ValidationError


def example_context_manager():
    """Example: Using context manager for automatic cleanup."""
    print("\n" + "=" * 70)
    print("Example: Context Manager Pattern")
    print("=" * 70)

    print("Using context manager ensures proper cleanup...")

    # Context manager automatically closes the driver
    with AmplitudeDriver.from_env() as driver:
        events = [
            {
                "user_id": "user_ctx_001",
                "event_type": "context_test"
            }
        ]

        result = driver.create_batch(events)
        print(f"✓ Events ingested: {result.get('events_ingested')}")
        print("✓ Driver will auto-close when exiting block")


def example_retry_configuration():
    """Example: Configure retry behavior."""
    print("\n" + "=" * 70)
    print("Example: Retry Configuration")
    print("=" * 70)

    print("Demonstrating different retry configurations...\n")

    # Conservative: Fewer retries
    print("1. Conservative (1 retry, 10s timeout)")
    with AmplitudeDriver.from_env(max_retries=1, timeout=10) as driver:
        events = [{"user_id": "user_1", "event_type": "test"}]
        result = driver.create_batch(events)
        print(f"   ✓ Success: {result.get('events_ingested')} events")

    # Aggressive: More retries for high-reliability scenarios
    print("\n2. Aggressive (5 retries, 60s timeout)")
    with AmplitudeDriver.from_env(max_retries=5, timeout=60) as driver:
        events = [{"user_id": "user_2", "event_type": "test"}]
        result = driver.create_batch(events)
        print(f"   ✓ Success: {result.get('events_ingested')} events")

    # Default
    print("\n3. Default (3 retries, 30s timeout)")
    with AmplitudeDriver.from_env() as driver:
        events = [{"user_id": "user_3", "event_type": "test"}]
        result = driver.create_batch(events)
        print(f"   ✓ Success: {result.get('events_ingested')} events")


def example_debug_logging():
    """Example: Enable debug logging for troubleshooting."""
    print("\n" + "=" * 70)
    print("Example: Debug Logging")
    print("=" * 70)

    print("Enabling debug mode to see detailed request/response logging...\n")

    with AmplitudeDriver.from_env(debug=True) as driver:
        events = [
            {
                "user_id": "user_debug_001",
                "event_type": "debug_test",
                "event_properties": {"test": True}
            }
        ]

        print("Uploading events (check debug output above)...")
        result = driver.create_batch(events)
        print(f"✓ Events ingested: {result.get('events_ingested')}")


def example_adaptive_batching():
    """Example: Adaptive batch sizing based on response."""
    print("\n" + "=" * 70)
    print("Example: Adaptive Batch Sizing")
    print("=" * 70)

    print("Processing events with dynamic batch sizing...\n")

    try:
        driver = AmplitudeDriver.from_env()

        total_events = 3500
        current_batch_size = 2000  # Start with max

        sent = 0
        batch_num = 0

        while sent < total_events:
            batch_end = min(sent + current_batch_size, total_events)
            batch = [
                {
                    "user_id": f"user_{i}",
                    "event_type": "adaptive_test"
                }
                for i in range(sent, batch_end)
            ]

            batch_num += 1
            print(f"Batch {batch_num}: Sending {len(batch)} events... ", end="", flush=True)

            try:
                result = driver.create_batch(batch)
                print(f"✓ {result.get('events_ingested')} ingested")
                sent = batch_end

            except RateLimitError as e:
                # Reduce batch size and retry
                print(f"Rate limited, reducing batch size...")
                current_batch_size = max(500, current_batch_size // 2)
                wait_time = e.details.get('retry_after', 5)
                print(f"  Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

            except ValidationError as e:
                # Batch too large, reduce
                print(f"Batch too large, reducing size...")
                current_batch_size = max(500, current_batch_size // 2)

        print(f"\n✓ All {sent} events sent successfully")

    finally:
        driver.close()


def example_production_pattern():
    """Example: Production-ready error handling pattern."""
    print("\n" + "=" * 70)
    print("Example: Production-Ready Pattern")
    print("=" * 70)

    def send_events_reliably(events, max_attempts=3):
        """Send events with production-grade error handling."""
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            try:
                with AmplitudeDriver.from_env() as driver:
                    result = driver.create_batch(events)
                    return {
                        "success": True,
                        "ingested": result.get('events_ingested'),
                        "attempt": attempt
                    }

            except RateLimitError as e:
                wait_time = e.details.get('retry_after', 5)
                print(f"  Attempt {attempt}: Rate limited. Waiting {wait_time}s...")
                if attempt < max_attempts:
                    time.sleep(wait_time)

            except ValidationError as e:
                print(f"  Attempt {attempt}: Validation error: {e.message}")
                return {
                    "success": False,
                    "error": "validation_error",
                    "message": e.message
                }

            except Exception as e:
                print(f"  Attempt {attempt}: Unexpected error: {e}")
                if attempt < max_attempts:
                    time.sleep(2)  # Brief pause before retry

        return {
            "success": False,
            "error": "max_attempts_exceeded",
            "attempts": max_attempts
        }

    print("Sending events with production error handling...\n")

    events = [
        {
            "user_id": "user_prod_001",
            "event_type": "production_test",
            "event_properties": {"environment": "production"}
        }
    ]

    result = send_events_reliably(events, max_attempts=3)
    print(f"Result: {result}")


def example_discovery_flow():
    """Example: Capability discovery pattern (useful for agents)."""
    print("\n" + "=" * 70)
    print("Example: Discovery Flow (Agent Integration)")
    print("=" * 70)

    print("Discovering driver capabilities (as an agent would)...\n")

    with AmplitudeDriver.from_env() as driver:
        # Step 1: Check capabilities
        print("1. Checking driver capabilities...")
        caps = driver.get_capabilities()
        print(f"   - Read operations: {caps.read}")
        print(f"   - Write operations: {caps.write}")
        print(f"   - Update operations: {caps.update}")
        print(f"   - Batch operations: {caps.batch_operations}")
        print(f"   - Max page size: {caps.max_page_size}")

        # Step 2: Discover available objects
        print("\n2. Discovering available objects...")
        objects = driver.list_objects()
        print(f"   - Available: {', '.join(objects)}")

        # Step 3: Explore object schema
        print("\n3. Exploring 'events' schema...")
        fields = driver.get_fields("events")
        important_fields = ["user_id", "device_id", "event_type", "time", "event_properties"]
        for field in important_fields:
            if field in fields:
                info = fields[field]
                print(f"   - {field}: {info.get('type')} " +
                      f"(req: {info.get('required', False)})")

        # Step 4: Make decision
        print("\n4. Decision: Can perform batch write operations ✓")


def example_monitoring():
    """Example: Rate limit and performance monitoring."""
    print("\n" + "=" * 70)
    print("Example: Monitoring and Metrics")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        print("Checking rate limit status...")
        status = driver.get_rate_limit_status()

        print(f"\nRate limit status:")
        for key, value in status.items():
            print(f"  {key}: {value}")

        # Monitor performance
        print("\nMonitoring batch upload performance...")

        events_sizes = [100, 500, 1000, 2000]

        for size in events_sizes:
            events = [
                {"user_id": f"user_{i}", "event_type": "perf_test"}
                for i in range(size)
            ]

            start = time.time()
            result = driver.create_batch(events)
            elapsed = time.time() - start

            events_per_sec = size / elapsed
            print(f"  {size:4d} events: {elapsed:.3f}s ({events_per_sec:.0f} events/sec)")

    finally:
        driver.close()


def main():
    """Run all advanced examples."""
    print("=" * 70)
    print("Amplitude Driver - Advanced Usage Examples")
    print("=" * 70)

    # Run examples
    example_context_manager()
    example_retry_configuration()
    example_debug_logging()
    example_adaptive_batching()
    example_production_pattern()
    example_discovery_flow()
    example_monitoring()

    print("\n" + "=" * 70)
    print("Advanced usage examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
