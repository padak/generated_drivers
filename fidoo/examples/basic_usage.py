"""
Example: Basic Usage - Query and Read Operations

This example demonstrates:
- Loading credentials from environment
- Discovering available objects
- Querying objects
- Processing results
- Resource cleanup

Run:
    export FIDOO_API_KEY="your_api_key_here"
    python basic_usage.py
"""

from fidoo8 import Fidoo8Driver


def main():
    """Demonstrate basic driver usage"""

    # Initialize driver from environment
    # Requires: FIDOO_API_KEY environment variable
    client = Fidoo8Driver.from_env()

    try:
        # 1. Discover available objects
        print("=" * 70)
        print("STEP 1: Discover Available Objects")
        print("=" * 70)

        objects = client.list_objects()
        print(f"\nAvailable objects in Fidoo API ({len(objects)} total):")
        for i, obj in enumerate(objects, 1):
            print(f"  {i:2d}. {obj}")

        # 2. Get field schema for an object
        print("\n" + "=" * 70)
        print("STEP 2: Inspect Object Schema")
        print("=" * 70)

        fields = client.get_fields("User")
        print(f"\nUser object has {len(fields)} fields:")
        for field_name, field_info in list(fields.items())[:5]:  # Show first 5
            field_type = field_info.get("type", "unknown")
            description = field_info.get("description", "")
            print(f"  {field_name:<25} {field_type:<15} {description}")
        print(f"  ... and {len(fields) - 5} more fields")

        # 3. Query an object
        print("\n" + "=" * 70)
        print("STEP 3: Query Users")
        print("=" * 70)

        users = client.read("User", limit=10)
        print(f"\nFetched {len(users)} users:")
        print()

        for i, user in enumerate(users, 1):
            first_name = user.get("firstName", "N/A")
            last_name = user.get("lastName", "N/A")
            email = user.get("email", "N/A")
            status = user.get("userState", "N/A")
            deactivated = user.get("deactivated", False)

            status_marker = "[DEACTIVATED]" if deactivated else f"[{status.upper()}]"

            print(f"  {i:2d}. {first_name} {last_name} ({email})")
            print(f"      Status: {status_marker}")
            print()

        # 4. Get driver capabilities
        print("=" * 70)
        print("STEP 4: Check Driver Capabilities")
        print("=" * 70)

        caps = client.get_capabilities()
        print(f"\nDriver Capabilities:")
        print(f"  Read:               {caps.read}")
        print(f"  Write:              {caps.write}")
        print(f"  Update:             {caps.update}")
        print(f"  Delete:             {caps.delete}")
        print(f"  Pagination:         {caps.pagination.value}")
        print(f"  Max page size:      {caps.max_page_size}")
        print(f"  Batch operations:   {caps.batch_operations}")

        print("\n" + "=" * 70)
        print("✅ Basic usage example completed successfully!")
        print("=" * 70)

    finally:
        # Always close the client
        client.close()


if __name__ == "__main__":
    main()
