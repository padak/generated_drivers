#!/usr/bin/env python3
"""
Basic Usage Example

Demonstrates fundamental driver operations:
- Initialize driver from environment
- List available resources
- Get resource schema
- Read data from an endpoint
- Cleanup

This is the simplest way to get started with the PostHog driver.

Requirements:
    - POSTHOG_API_KEY environment variable set

Usage:
    python basic_usage.py
"""

from posthog_driver import PostHogDriver


def main():
    """Main example function."""
    print("=" * 70)
    print("PostHog Driver - Basic Usage Example")
    print("=" * 70)

    # Initialize driver from environment variables
    print("\n1. Initializing driver from environment...")
    driver = PostHogDriver.from_env()
    print("   ✓ Driver initialized successfully")

    try:
        # List available resources
        print("\n2. Listing available resources...")
        objects = driver.list_objects()
        print(f"   Available resources ({len(objects)}):")
        for i, obj in enumerate(objects, 1):
            print(f"     {i}. {obj}")

        # Get field schema for a specific resource
        print("\n3. Getting field schema for 'dashboards'...")
        fields = driver.get_fields("dashboards")
        print(f"   Fields ({len(fields)}):")
        for field_name, field_info in list(fields.items())[:5]:
            required = "required" if field_info.get("required") else "optional"
            print(f"     - {field_name}: {field_info.get('type')} ({required})")
        if len(fields) > 5:
            print(f"     ... and {len(fields) - 5} more fields")

        # Check driver capabilities
        print("\n4. Checking driver capabilities...")
        capabilities = driver.get_capabilities()
        print(f"   Read: {capabilities.read}")
        print(f"   Write: {capabilities.write}")
        print(f"   Update: {capabilities.update}")
        print(f"   Delete: {capabilities.delete}")
        print(f"   Batch Operations: {capabilities.batch_operations}")
        print(f"   Max Page Size: {capabilities.max_page_size}")

        # Read data from an endpoint
        print("\n5. Reading dashboards...")
        dashboards = driver.read("/dashboards", limit=5)
        print(f"   Found {len(dashboards)} dashboards")

        if dashboards:
            print("\n   First dashboard:")
            dashboard = dashboards[0]
            print(f"     ID: {dashboard.get('id')}")
            print(f"     Name: {dashboard.get('name')}")
            print(f"     Created: {dashboard.get('created_at')}")

    finally:
        # Always close the driver
        print("\n6. Closing driver...")
        driver.close()
        print("   ✓ Driver closed")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
