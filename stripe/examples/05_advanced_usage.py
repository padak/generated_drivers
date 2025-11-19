"""
Example 5: Advanced Usage

Demonstrates advanced driver patterns:
- Discovery and dynamic queries
- Chaining operations
- Multi-resource workflows
- Advanced error recovery
- Performance optimization

This example shows sophisticated patterns for
production use cases.
"""

from stripe_driver import (
    StripeDriver,
    ObjectNotFoundError,
    ValidationError,
    RateLimitError,
)


def discover_and_query():
    """Discover available resources and query them."""
    print("\n[1] Discovery and Dynamic Querying")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        # Discover available resources
        print("  Discovering available resources...")
        resources = client.list_objects()
        print(f"  ✓ Found {len(resources)} resource types")

        # Show capabilities
        print("\n  Checking driver capabilities...")
        caps = client.get_capabilities()
        print(f"    ✓ Read operations: {caps.read}")
        print(f"    ✓ Write operations: {caps.write}")
        print(f"    ✓ Update operations: {caps.update}")
        print(f"    ✓ Delete operations: {caps.delete}")
        print(f"    ✓ Pagination style: {caps.pagination.value}")
        print(f"    ✓ Max page size: {caps.max_page_size}")

        # Dynamically query available resources
        print("\n  Querying available resources...")
        resources_to_query = ["products", "customers", "invoices"]

        for resource in resources_to_query:
            if resource in resources:
                try:
                    items = client.read(resource, limit=1)
                    print(f"    ✓ {resource}: {len(items)} items available")
                except Exception as e:
                    print(f"    ✗ {resource}: {type(e).__name__}")

    finally:
        client.close()


def multi_resource_workflow():
    """Demonstrate workflow spanning multiple resources."""
    print("\n[2] Multi-Resource Workflow")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Workflow: Summary Report")
        print("  " + "-" * 66)

        # Get product statistics
        print("\n  Step 1: Gather product statistics")
        products = client.read("products", limit=50)
        active_products = sum(1 for p in products if p.get("active", False))
        print(f"    ✓ Total products queried: {len(products)}")
        print(f"    ✓ Active products: {active_products}")

        # Get customer statistics
        print("\n  Step 2: Gather customer statistics")
        customers = client.read("customers", limit=50)
        print(f"    ✓ Total customers queried: {len(customers)}")

        # Get invoice statistics
        print("\n  Step 3: Gather invoice statistics")
        invoices = client.read("invoices", limit=50)
        paid_invoices = sum(1 for i in invoices if i.get("paid", False))
        print(f"    ✓ Total invoices queried: {len(invoices)}")
        print(f"    ✓ Paid invoices: {paid_invoices}")

        # Generate report
        print("\n  Summary Report:")
        print(f"    Products:    {len(products)}")
        print(f"    Customers:   {len(customers)}")
        print(f"    Invoices:    {len(invoices)} (Paid: {paid_invoices})")

    finally:
        client.close()


def field_discovery():
    """Discover and display field schema."""
    print("\n[3] Field Discovery and Schema")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        resources_to_inspect = ["product", "customer", "invoice"]

        for resource in resources_to_inspect:
            print(f"\n  Schema for '{resource}':")

            try:
                fields = client.get_fields(resource)
                required_fields = [
                    name
                    for name, info in fields.items()
                    if info.get("required", False)
                ]

                print(f"    Total fields: {len(fields)}")
                print(f"    Required fields: {len(required_fields)}")
                if required_fields:
                    print(f"      - {', '.join(required_fields[:3])}")

            except ObjectNotFoundError as e:
                print(f"    ✗ Not found: {e.message}")

    finally:
        client.close()


def resilient_processing():
    """Demonstrate resilient processing with error recovery."""
    print("\n[4] Resilient Processing with Error Recovery")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Processing with error recovery...")

        success_count = 0
        error_count = 0
        resources_to_process = ["products", "customers", "invalid_resource"]

        for resource in resources_to_process:
            try:
                print(f"\n  Processing: {resource}")

                # Try to read from resource
                items = client.read(resource, limit=5)
                print(f"    ✓ Success: {len(items)} items")
                success_count += 1

            except ObjectNotFoundError as e:
                print(f"    ✗ Not found: {e.message}")
                error_count += 1

            except ValidationError as e:
                print(f"    ✗ Validation error: {e.message}")
                error_count += 1

            except RateLimitError as e:
                retry_after = e.details.get("retry_after", 60)
                print(f"    ✗ Rate limited, retry after {retry_after}s")
                error_count += 1

            except Exception as e:
                print(f"    ✗ Unexpected error: {type(e).__name__}")
                error_count += 1

        print(f"\n  Summary:")
        print(f"    Successful: {success_count}")
        print(f"    Failed: {error_count}")
        print(f"    Total: {success_count + error_count}")

    finally:
        client.close()


def advanced_pagination():
    """Demonstrate advanced pagination techniques."""
    print("\n[5] Advanced Pagination Techniques")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Technique 1: Collecting data across batches")
        print("    Processing in batches of 30...")

        all_data = []
        batch_count = 0

        for batch in client.read_batched("products", batch_size=30):
            batch_count += 1
            all_data.extend(batch)

            print(f"    Batch {batch_count}: {len(batch)} items (Total: {len(all_data)})")

            if batch_count >= 3:  # Limit for demo
                break

        print(f"  ✓ Collected {len(all_data)} items across {batch_count} batches")

        print("\n  Technique 2: Filtering during pagination")
        print("    Looking for items matching criteria...")

        matching_items = []
        for batch in client.read_batched("products", batch_size=50):
            # Filter items during iteration
            filtered = [
                item for item in batch if item.get("active", False) is True
            ]
            matching_items.extend(filtered)

            print(f"    Batch: {len(batch)} items, {len(filtered)} matching")

            if len(matching_items) >= 10:
                break

        print(f"  ✓ Found {len(matching_items)} matching items")

    finally:
        client.close()


def configuration_options():
    """Demonstrate advanced configuration."""
    print("\n[6] Advanced Configuration Options")
    print("-" * 70)

    print("  Configuration Option 1: Custom Timeout")
    print("    Creating client with 60-second timeout...")
    client1 = StripeDriver.from_env(timeout=60)
    print("    ✓ Client created with timeout=60")
    client1.close()

    print("\n  Configuration Option 2: Debug Mode")
    print("    Creating client with debug logging...")
    client2 = StripeDriver.from_env(debug=True)
    print("    ✓ Client created with debug=True")
    print("    (Debug output would show API calls)")
    client2.close()

    print("\n  Configuration Option 3: Retry Configuration")
    print("    Creating client with aggressive retry (5 attempts)...")
    client3 = StripeDriver.from_env(max_retries=5)
    print("    ✓ Client created with max_retries=5")
    client3.close()

    print("\n  ✓ All configuration options available")


def performance_optimization():
    """Demonstrate performance optimization patterns."""
    print("\n[7] Performance Optimization Patterns")
    print("-" * 70)

    import time

    client = StripeDriver.from_env()

    try:
        print("  Pattern 1: Batch size optimization")
        batch_sizes = [10, 50, 100]

        for batch_size in batch_sizes:
            start = time.time()
            items_counted = 0

            for batch in client.read_batched("products", batch_size=batch_size):
                items_counted += len(batch)
                if items_counted >= 100:
                    break

            elapsed = time.time() - start
            print(f"    batch_size={batch_size}: {items_counted} items in {elapsed:.2f}s")

        print("\n  Pattern 2: Memory efficiency")
        print("    Using read_batched for large result sets...")
        memory_efficient_count = 0
        for batch in client.read_batched("products", batch_size=50):
            # Process only what's needed, don't store all
            memory_efficient_count += len(batch)
            if memory_efficient_count >= 200:
                break

        print(f"    ✓ Processed {memory_efficient_count} items efficiently")

        print("\n  Pattern 3: Concurrent request optimization")
        print("    Querying multiple resources...")
        start = time.time()

        resources_data = {}
        for resource_type in ["products", "customers", "invoices"]:
            data = client.read(resource_type, limit=20)
            resources_data[resource_type] = len(data)

        elapsed = time.time() - start
        print(f"    ✓ Queried 3 resources in {elapsed:.2f}s")

    finally:
        client.close()


def main():
    """Run all advanced usage examples."""
    print("=" * 70)
    print("Example 5: Advanced Usage Patterns")
    print("=" * 70)

    discover_and_query()
    multi_resource_workflow()
    field_discovery()
    resilient_processing()
    advanced_pagination()
    configuration_options()
    performance_optimization()

    print("\n" + "=" * 70)
    print("✓ Advanced usage examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
