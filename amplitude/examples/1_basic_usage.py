#!/usr/bin/env python3
"""
Example 1: Basic Usage

Demonstrates basic driver setup and common operations:
- Initialize driver from environment
- Discover available objects and fields
- Upload a single event
- Cleanup

Run this example:
    export AMPLITUDE_API_KEY="your_api_key"
    python 1_basic_usage.py
"""

from amplitude import AmplitudeDriver


def main():
    """Run basic usage example."""
    print("=" * 70)
    print("Amplitude Driver - Basic Usage Example")
    print("=" * 70)

    # Step 1: Initialize driver from environment variables
    print("\n1. Initializing driver from environment...")
    driver = AmplitudeDriver.from_env()
    print("   ✓ Driver initialized successfully")

    # Step 2: Discover driver capabilities
    print("\n2. Discovering driver capabilities...")
    capabilities = driver.get_capabilities()
    print(f"   Read operations: {capabilities.read}")
    print(f"   Write operations: {capabilities.write}")
    print(f"   Update operations: {capabilities.update}")
    print(f"   Batch operations: {capabilities.batch_operations}")
    print(f"   Max page size: {capabilities.max_page_size}")

    # Step 3: Discover available objects
    print("\n3. Discovering available objects...")
    objects = driver.list_objects()
    print(f"   Available objects: {', '.join(objects)}")

    # Step 4: Get field schema for events
    print("\n4. Exploring 'events' object schema...")
    fields = driver.get_fields("events")
    print(f"   Total fields: {len(fields)}")
    print("   Key fields:")
    for field_name in ["user_id", "device_id", "event_type", "time"]:
        if field_name in fields:
            field = fields[field_name]
            print(f"     - {field_name}: {field.get('type')} " +
                  f"(required: {field.get('required', False)})")

    # Step 5: Upload a single event
    print("\n5. Uploading a single event...")
    import time
    event = {
        "user_id": "user_example_001",
        "event_type": "page_view",
        "time": int(time.time() * 1000),  # Current time in milliseconds
        "event_properties": {
            "page": "/products",
            "referrer": "google"
        }
    }
    print(f"   Event: {event}")

    try:
        result = driver.create("events", event)
        print(f"   ✓ Event uploaded successfully")
        print(f"   Response code: {result.get('code')}")
        print(f"   Events ingested: {result.get('events_ingested')}")
    except Exception as e:
        print(f"   ✗ Error uploading event: {e}")

    # Step 6: Cleanup
    print("\n6. Cleaning up...")
    driver.close()
    print("   ✓ Driver closed successfully")

    print("\n" + "=" * 70)
    print("Basic usage example completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
