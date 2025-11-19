#!/usr/bin/env python3
"""
Example 3: Batch Operations

Demonstrates efficient bulk operations:
- Upload multiple events in a single batch
- Process large datasets by splitting into batches
- Monitor ingestion statistics
- Handle batch errors

Run this example:
    export AMPLITUDE_API_KEY="your_api_key"
    python 3_batch_operations.py
"""

import time
from amplitude import AmplitudeDriver
from amplitude.exceptions import ValidationError, RateLimitError


def example_simple_batch():
    """Example: Upload a simple batch of events."""
    print("\n" + "=" * 70)
    print("Example: Simple Batch Upload")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Create a batch of events
        events = [
            {
                "user_id": "user_1",
                "event_type": "page_view",
                "time": int(time.time() * 1000),
                "event_properties": {
                    "page": "/home",
                    "referrer": "direct"
                },
                "user_properties": {
                    "plan": "premium"
                }
            },
            {
                "user_id": "user_2",
                "event_type": "button_click",
                "time": int(time.time() * 1000),
                "event_properties": {
                    "button_id": "signup",
                    "section": "header"
                }
            },
            {
                "user_id": "user_3",
                "event_type": "purchase",
                "time": int(time.time() * 1000),
                "event_properties": {
                    "product_id": "prod_123",
                    "amount": 99.99
                }
            },
        ]

        print(f"Uploading batch of {len(events)} events...")
        result = driver.create_batch(events)

        print(f"✓ Batch uploaded successfully")
        print(f"  Events ingested: {result.get('events_ingested')}")
        print(f"  Payload size: {result.get('payload_size_bytes')} bytes")
        print(f"  Server time: {result.get('server_upload_time')}")

    finally:
        driver.close()


def example_large_batch_processing():
    """Example: Process large dataset by splitting into batches."""
    print("\n" + "=" * 70)
    print("Example: Large Batch Processing")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Simulate a large dataset
        total_events = 5500  # More than 2 batches of 2000
        batch_size = 2000    # Max batch size

        print(f"Processing {total_events} events in batches of {batch_size}...")

        total_ingested = 0
        batches_sent = 0

        # Process events in batches
        for offset in range(0, total_events, batch_size):
            batch_end = min(offset + batch_size, total_events)
            current_batch_size = batch_end - offset

            # Generate batch of events
            batch = [
                {
                    "user_id": f"user_{i}",
                    "event_type": "generated_event",
                    "time": int(time.time() * 1000),
                    "event_properties": {
                        "batch_index": offset // batch_size,
                        "event_index": i - offset
                    }
                }
                for i in range(offset, batch_end)
            ]

            # Upload batch
            print(f"\n  Batch {batches_sent + 1}: Uploading {len(batch)} events...")
            try:
                result = driver.create_batch(batch)
                ingested = result.get('events_ingested', 0)
                total_ingested += ingested
                print(f"    ✓ Success: {ingested} events ingested")

            except RateLimitError as e:
                print(f"    ! Rate limited. Waiting {e.details['retry_after']}s...")
                time.sleep(e.details['retry_after'])
                # Retry this batch
                result = driver.create_batch(batch)
                ingested = result.get('events_ingested', 0)
                total_ingested += ingested
                print(f"    ✓ Success (after retry): {ingested} events ingested")

            batches_sent += 1

        print(f"\n✓ Batch processing completed")
        print(f"  Total batches: {batches_sent}")
        print(f"  Total events ingested: {total_ingested}")

    finally:
        driver.close()


def example_events_with_properties():
    """Example: Batch with various event and user properties."""
    print("\n" + "=" * 70)
    print("Example: Events with User Properties")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        events = [
            {
                "user_id": "user_premium_1",
                "device_id": "device_abc123",
                "event_type": "feature_used",
                "time": int(time.time() * 1000),
                "event_properties": {
                    "feature_name": "advanced_analytics",
                    "duration_seconds": 45.5,
                    "success": True
                },
                "user_properties": {
                    "plan": "premium",
                    "signup_date": "2024-01-15",
                    "credits": 1000
                }
            },
            {
                "user_id": "user_free_1",
                "device_id": "device_xyz789",
                "event_type": "upgrade_viewed",
                "time": int(time.time() * 1000),
                "event_properties": {
                    "upgrade_tier": "premium",
                    "shown_from": "settings_page"
                },
                "user_properties": {
                    "plan": "free",
                    "signup_date": "2024-11-01",
                    "credits": 0
                }
            },
        ]

        print(f"Uploading batch with user properties...")
        result = driver.create_batch(events)

        print(f"✓ Batch uploaded successfully")
        print(f"  Events ingested: {result.get('events_ingested')}")

    finally:
        driver.close()


def example_batch_error_handling():
    """Example: Handle batch-specific errors."""
    print("\n" + "=" * 70)
    print("Example: Batch Error Handling")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # Scenario 1: Too many events
        print("\nScenario 1: Batch exceeds size limit")
        try:
            huge_batch = [
                {"user_id": f"user_{i}", "event_type": "test"}
                for i in range(3000)  # Exceeds 2000 limit
            ]
            driver.create_batch(huge_batch)
        except ValidationError as e:
            print(f"  ✓ Caught error: {e.message}")
            print(f"    Limit: {e.details.get('maximum')}, Provided: {e.details.get('provided')}")

        # Scenario 2: Empty batch
        print("\nScenario 2: Empty batch")
        try:
            driver.create_batch([])  # Empty batch
        except ValidationError as e:
            print(f"  ✓ Caught error: {e.message}")

        # Scenario 3: Valid batch
        print("\nScenario 3: Valid batch")
        small_batch = [
            {"user_id": "user_test", "event_type": "test"}
        ]
        result = driver.create_batch(small_batch)
        print(f"  ✓ Success: {result.get('events_ingested')} events ingested")

    finally:
        driver.close()


def example_batch_with_deduplication():
    """Example: Batch with insert_id for deduplication."""
    print("\n" + "=" * 70)
    print("Example: Batch with Deduplication (insert_id)")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        import uuid

        events = [
            {
                "user_id": "user_dup_1",
                "event_type": "payment_processed",
                "time": int(time.time() * 1000),
                "insert_id": "payment_20250119_001",  # Unique ID for deduplication
                "event_properties": {
                    "amount": 50.00,
                    "currency": "USD"
                }
            },
            {
                "user_id": "user_dup_2",
                "event_type": "order_shipped",
                "time": int(time.time() * 1000),
                "insert_id": str(uuid.uuid4()),  # Generated UUID
                "event_properties": {
                    "order_id": "ord_12345",
                    "tracking_number": "TRK987654"
                }
            },
        ]

        print("Uploading batch with insert_id (deduplication)...")
        print("Note: Amplitude deduplicates events with same insert_id within 7 days")

        result = driver.create_batch(events)
        print(f"✓ Batch uploaded: {result.get('events_ingested')} events ingested")

    finally:
        driver.close()


def main():
    """Run all batch operation examples."""
    print("=" * 70)
    print("Amplitude Driver - Batch Operations Examples")
    print("=" * 70)

    # Run examples
    example_simple_batch()
    example_large_batch_processing()
    example_events_with_properties()
    example_batch_error_handling()
    example_batch_with_deduplication()

    print("\n" + "=" * 70)
    print("Batch operations examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
