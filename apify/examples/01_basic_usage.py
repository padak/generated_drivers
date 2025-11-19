"""
Example 1: Basic Usage

Demonstrates fundamental ApifyDriver operations:
- Initialize driver from environment
- List available resources
- Query resources
- Handle basic errors
- Cleanup

Prerequisites:
    export APIFY_API_TOKEN="your_token_here"

Run:
    python examples/01_basic_usage.py
"""

from apify_driver import ApifyDriver, ObjectNotFoundError, AuthenticationError


def main():
    """Basic ApifyDriver usage example"""

    # Initialize client from environment variables
    # Sets: api_url, api_key, timeout, max_retries, debug
    client = ApifyDriver.from_env()

    try:
        print("=" * 70)
        print("EXAMPLE 1: Basic ApifyDriver Usage")
        print("=" * 70)

        # ===== DISCOVERY =====
        print("\n1. DISCOVERY - What resources are available?")
        print("-" * 70)

        resources = client.list_objects()
        print(f"Available resources ({len(resources)}):")
        for resource in resources:
            print(f"  • {resource}")

        # ===== GET SCHEMA =====
        print("\n2. SCHEMA - What fields does each resource have?")
        print("-" * 70)

        actor_fields = client.get_fields("actors")
        print(f"Actor fields ({len(actor_fields)}):")
        for field_name, field_info in list(actor_fields.items())[:5]:
            print(f"  • {field_name}: {field_info.get('type', 'unknown')}")
        print(f"  ... and {len(actor_fields) - 5} more fields")

        # ===== CAPABILITIES =====
        print("\n3. CAPABILITIES - What can the driver do?")
        print("-" * 70)

        capabilities = client.get_capabilities()
        print(f"Read operations: {capabilities.read}")
        print(f"Write operations: {capabilities.write}")
        print(f"Update operations: {capabilities.update}")
        print(f"Delete operations: {capabilities.delete}")
        print(f"Batch operations: {capabilities.batch_operations}")
        print(f"Pagination style: {capabilities.pagination.value}")
        print(f"Max page size: {capabilities.max_page_size}")

        # ===== BASIC QUERY =====
        print("\n4. BASIC QUERY - Get actors")
        print("-" * 70)

        # Simple read without pagination
        actors = client.read("/actors", limit=3)
        print(f"Retrieved {len(actors)} actors:")
        for actor in actors:
            actor_name = actor.get("name", "Unknown")
            actor_id = actor.get("id", "N/A")
            print(f"  • {actor_name} (ID: {actor_id})")

        # ===== SUCCESS MESSAGE =====
        print("\n" + "=" * 70)
        print("✓ Basic usage example completed successfully")
        print("=" * 70)

    except AuthenticationError as e:
        print(f"\n❌ Authentication failed: {e.message}")
        print("Make sure APIFY_API_TOKEN environment variable is set")

    except ObjectNotFoundError as e:
        print(f"\n❌ Resource not found: {e.message}")

    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")

    finally:
        # Always cleanup
        client.close()
        print("\n✓ Client closed")


if __name__ == "__main__":
    main()
