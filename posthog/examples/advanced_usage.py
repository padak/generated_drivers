#!/usr/bin/env python3
"""
Advanced Usage Example

Demonstrates complex patterns and techniques:
- Combining multiple operations
- Complex filtering and aggregation
- Performance optimization
- Debug mode for troubleshooting
- Custom endpoint calls
- Advanced error recovery

This example shows how to use the driver for more complex scenarios.

Requirements:
    - POSTHOG_API_KEY environment variable set

Usage:
    python advanced_usage.py
"""

from posthog_driver import PostHogDriver, DriverError, RateLimitError
import time
from datetime import datetime


def example_combined_operations():
    """Combine read, filter, and write operations."""
    print("\n" + "=" * 70)
    print("1. Combined Operations: Read → Filter → Create")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Scenario: Copy dashboards with specific naming pattern")
        print()

        # Read existing dashboards
        print("  Step 1: Reading existing dashboards...")
        dashboards = driver.read("/dashboards", limit=10)
        print(f"    Found {len(dashboards)} dashboards")

        # Filter dashboards
        print(f"\n  Step 2: Filtering dashboards...")
        filtered = [d for d in dashboards if "test" not in d.get("name", "").lower()]
        print(f"    Filtered: {len(filtered)} dashboards (excluded test dashboards)")

        # Create summary
        print(f"\n  Step 3: Dashboard Summary")
        for i, dashboard in enumerate(filtered[:3], 1):
            print(f"    {i}. {dashboard.get('name')}")
            print(f"       Created: {dashboard.get('created_at')}")

        print(f"\n  ✓ Combined operations completed!")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_advanced_filtering_and_aggregation():
    """Demonstrate advanced filtering and aggregation during batch processing."""
    print("\n" + "=" * 70)
    print("2. Advanced Filtering and Aggregation")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Scenario: Process events and build analytics")
        print()

        # Statistics to collect
        stats = {
            "total_events": 0,
            "event_types": {},
            "processed_batches": 0,
            "start_time": time.time(),
        }

        print("  Processing events in batches...")

        for batch in driver.read_batched("/events", batch_size=100):
            stats["processed_batches"] += 1

            # Process each event
            for event in batch:
                event_type = event.get("event", "unknown")

                # Aggregate
                if event_type not in stats["event_types"]:
                    stats["event_types"][event_type] = {
                        "count": 0,
                        "first_seen": None,
                        "last_seen": None,
                    }

                stats["event_types"][event_type]["count"] += 1
                stats["total_events"] += 1

            # Stop after 5 batches for demo
            if stats["processed_batches"] >= 5:
                break

        elapsed = time.time() - stats["start_time"]

        # Display results
        print(f"\n  ✓ Statistics Collected:")
        print(f"    Total events: {stats['total_events']}")
        print(f"    Batches processed: {stats['processed_batches']}")
        print(f"    Event types found: {len(stats['event_types'])}")
        print(f"    Time elapsed: {elapsed:.2f}s")

        if stats["event_types"]:
            print(f"\n  Top event types:")
            sorted_types = sorted(
                stats["event_types"].items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )
            for event_type, data in sorted_types[:5]:
                percentage = (data["count"] / stats["total_events"]) * 100
                print(f"    - {event_type}: {data['count']} ({percentage:.1f}%)")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_performance_optimization():
    """Demonstrate performance optimization techniques."""
    print("\n" + "=" * 70)
    print("3. Performance Optimization")
    print("=" * 70)

    print("  Technique 1: Batch Size Optimization")
    print("  " + "-" * 66)

    driver = PostHogDriver.from_env()

    try:
        batch_sizes = [10, 50, 100]

        for batch_size in batch_sizes:
            start_time = time.time()
            total_events = 0
            batches = 0

            for batch in driver.read_batched("/events", batch_size=batch_size):
                batches += 1
                total_events += len(batch)

                if batches >= 3:  # Only 3 batches for timing
                    break

            elapsed = time.time() - start_time

            rate = total_events / elapsed if elapsed > 0 else 0
            print(f"  Batch size {batch_size:3d}: {total_events:4d} events "
                  f"in {elapsed:.3f}s ({rate:.0f} events/sec)")

        print(f"\n  Technique 2: Query Optimization")
        print("  " + "-" * 66)

        # Read with optimized limit
        print(f"  Reading dashboards with optimized pagination...")
        dashboards = driver.read("/dashboards", limit=50, offset=0)
        print(f"    ✓ Retrieved {len(dashboards)} dashboards efficiently")

        print(f"\n  ✓ Performance optimization techniques demonstrated!")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_debug_mode_troubleshooting():
    """Demonstrate debug mode for troubleshooting."""
    print("\n" + "=" * 70)
    print("4. Debug Mode for Troubleshooting")
    print("=" * 70)

    try:
        print("  Creating driver with debug=True...")
        driver = PostHogDriver.from_env(debug=True)

        print(f"\n  Making API call (check debug output)...")
        dashboards = driver.read("/dashboards", limit=2)

        print(f"\n  ✓ API call completed")
        print(f"    Retrieved {len(dashboards)} dashboards")

        driver.close()

    except Exception as e:
        print(f"  ✗ Error: {e}")


def example_custom_endpoint_calls():
    """Demonstrate direct endpoint calls."""
    print("\n" + "=" * 70)
    print("5. Custom Endpoint Calls (Low-Level Access)")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Making custom endpoint call...")

        # Call endpoint directly
        result = driver.call_endpoint(
            endpoint="/dashboards",
            method="GET",
            params={"limit": 5}
        )

        if isinstance(result, dict):
            # Extract data
            data = (
                result.get("results") or
                result.get("data") or
                result.get("items") or
                result
            )

            if isinstance(data, list):
                print(f"  ✓ Retrieved {len(data)} items from custom endpoint call")
                for item in data[:2]:
                    print(f"    - {item.get('name', 'Unnamed')}")
            else:
                print(f"  ✓ Custom endpoint call succeeded")
                print(f"    Response keys: {list(result.keys())[:5]}")

    except Exception as e:
        print(f"  ✗ Error in custom endpoint call: {e}")

    finally:
        driver.close()


def example_advanced_error_recovery():
    """Demonstrate advanced error recovery strategies."""
    print("\n" + "=" * 70)
    print("6. Advanced Error Recovery Strategies")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Strategy 1: Exponential Backoff with Retry")
        print("  " + "-" * 66)

        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                print(f"  Attempt {attempt + 1}/{max_retries}...")
                dashboards = driver.read("/dashboards", limit=5)
                print(f"  ✓ Success! Retrieved {len(dashboards)} dashboards")
                break

            except RateLimitError as e:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"  ✗ Rate limited, retrying in {delay}s...")
                    # time.sleep(delay)  # Skip actual sleep in demo
                else:
                    raise

        print(f"\n  Strategy 2: Graceful Degradation")
        print("  " + "-" * 66)

        # Try multiple operations in sequence, continue if one fails
        operations = [
            ("dashboards", "/dashboards"),
            ("datasets", "/datasets"),
            ("events", "/events"),
        ]

        successful = 0
        for name, endpoint in operations:
            try:
                print(f"  Attempting to read {name}...")
                data = driver.read(endpoint, limit=3)
                print(f"    ✓ Success: {len(data)} items")
                successful += 1

            except Exception as e:
                print(f"    ✗ Failed: {type(e).__name__}")
                # Continue with next operation

        print(f"\n  Summary: {successful}/{len(operations)} operations succeeded")

        print(f"\n  ✓ Advanced error recovery demonstrated!")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_monitoring_and_logging():
    """Demonstrate monitoring and logging patterns."""
    print("\n" + "=" * 70)
    print("7. Monitoring and Logging Patterns")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Monitoring: Tracking operation metrics")
        print("  " + "-" * 66)

        metrics = {
            "start_time": datetime.now(),
            "operations": [],
        }

        # Perform operations and track metrics
        operations_to_perform = [
            ("list_objects", lambda: driver.list_objects()),
            ("get_capabilities", lambda: driver.get_capabilities()),
            ("read_dashboards", lambda: driver.read("/dashboards", limit=5)),
        ]

        for op_name, op_func in operations_to_perform:
            try:
                start = time.time()
                result = op_func()
                elapsed = time.time() - start

                metrics["operations"].append({
                    "name": op_name,
                    "status": "success",
                    "duration": elapsed,
                    "timestamp": datetime.now().isoformat(),
                })

                print(f"  ✓ {op_name}: {elapsed:.3f}s")

            except Exception as e:
                metrics["operations"].append({
                    "name": op_name,
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })

                print(f"  ✗ {op_name}: Error - {str(e)[:50]}")

        # Print summary
        print(f"\n  Metrics Summary:")
        print(f"    Total operations: {len(metrics['operations'])}")

        successful = sum(1 for op in metrics["operations"] if op["status"] == "success")
        print(f"    Successful: {successful}")
        print(f"    Failed: {len(metrics['operations']) - successful}")

        total_time = sum(op.get("duration", 0) for op in metrics["operations"])
        print(f"    Total time: {total_time:.3f}s")

        print(f"\n  ✓ Monitoring and logging patterns demonstrated!")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def main():
    """Run all advanced usage examples."""
    print("=" * 70)
    print("PostHog Driver - Advanced Usage Examples")
    print("=" * 70)

    try:
        # Run demonstrations in order
        example_combined_operations()
        example_advanced_filtering_and_aggregation()
        example_performance_optimization()
        example_debug_mode_troubleshooting()
        example_custom_endpoint_calls()
        example_advanced_error_recovery()
        example_monitoring_and_logging()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")

    print("\n" + "=" * 70)
    print("All advanced usage examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
