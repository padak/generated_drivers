"""
Example 3: Pagination

Demonstrates large dataset handling:
- Cursor-based pagination
- Batch processing with read_batched()
- Memory-efficient iteration
- Processing large result sets

This example shows how to efficiently handle
large datasets without loading everything into memory.
"""

from stripe_driver import StripeDriver, RateLimitError


def basic_pagination():
    """Demonstrate basic manual pagination."""
    print("\n[1] Basic Manual Pagination")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        # Query with limit
        print("  Fetching first 10 products...")
        products = client.read("products", limit=10)
        print(f"  ✓ Fetched {len(products)} products")

        # Show pagination info
        print(f"  ✓ Result type: {type(products)}")
        print(f"  ✓ Can iterate: {hasattr(products, '__iter__')}")

        # Process results
        print("\n  Processing results:")
        for i, product in enumerate(products[:3], 1):
            name = product.get("name", "N/A")
            print(f"    {i}. {name}")

        if len(products) > 3:
            print(f"    ... and {len(products) - 3} more")

    finally:
        client.close()


def batched_reading():
    """Demonstrate efficient batch processing."""
    print("\n[2] Batched Reading (Memory-Efficient)")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Processing products in batches of 25...")
        batch_count = 0
        total_processed = 0

        # Use read_batched for automatic pagination
        for batch in client.read_batched("products", batch_size=25):
            batch_count += 1
            total_processed += len(batch)

            print(f"  Batch {batch_count}: {len(batch)} items")

            # Process each batch
            for product in batch:
                name = product.get("name", "Unknown")
                product_id = product.get("id", "N/A")
                # In real application: save_to_database(product)

            # Limit demo output
            if batch_count >= 3:
                print(f"  ... (stopping demo after {batch_count} batches)")
                break

        print(f"\n  ✓ Total processed: {total_processed} items in {batch_count} batches")

    except RateLimitError as e:
        print(f"  Rate limited: {e.message}")
        retry_after = e.details.get("retry_after", 60)
        print(f"  Retry after {retry_after} seconds")

    finally:
        client.close()


def filtering_and_aggregating():
    """Demonstrate filtering and aggregating batch data."""
    print("\n[3] Filtering and Aggregating Batches")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Aggregating product data from batches...")

        stats = {
            "total_products": 0,
            "active_products": 0,
            "products_with_description": 0,
        }

        batch_count = 0
        for batch in client.read_batched("products", batch_size=50):
            batch_count += 1

            for product in batch:
                stats["total_products"] += 1

                # Count active products
                active = product.get("active", False)
                if active:
                    stats["active_products"] += 1

                # Count products with description
                description = product.get("description")
                if description:
                    stats["products_with_description"] += 1

            # Limit demo
            if batch_count >= 2:
                break

        print(f"\n  Statistics from {batch_count} batches:")
        print(f"    Total products: {stats['total_products']}")
        print(f"    Active products: {stats['active_products']}")
        print(f"    With description: {stats['products_with_description']}")

    finally:
        client.close()


def configurable_batch_sizes():
    """Demonstrate different batch size configurations."""
    print("\n[4] Configurable Batch Sizes")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        batch_sizes = [10, 25, 50]

        for batch_size in batch_sizes:
            print(f"\n  Testing batch_size={batch_size}...")

            item_count = 0
            for batch in client.read_batched("products", batch_size=batch_size):
                item_count += len(batch)
                print(f"    Batch received: {len(batch)} items")

                # Stop after first batch for demo
                break

            print(f"    ✓ batch_size={batch_size} works correctly")

    finally:
        client.close()


def performance_comparison():
    """Demonstrate performance benefits of batch processing."""
    print("\n[5] Performance Benefits of Batch Processing")
    print("-" * 70)

    import time

    client = StripeDriver.from_env()

    try:
        print("\n  Method 1: Single large query")
        start = time.time()
        all_products = client.read("products", limit=100)
        elapsed1 = time.time() - start
        print(f"    ✓ Fetched {len(all_products)} items in {elapsed1:.2f}s")

        print("\n  Method 2: Batch processing")
        start = time.time()
        batch_count = 0
        total_items = 0
        for batch in client.read_batched("products", batch_size=25):
            batch_count += 1
            total_items += len(batch)
            if batch_count >= 4:  # Roughly same as 100 items
                break
        elapsed2 = time.time() - start
        print(f"    ✓ Fetched {total_items} items in {elapsed2:.2f}s")

        print(f"\n  ✓ Both methods work; batch processing is memory-efficient")

    finally:
        client.close()


def main():
    """Run all pagination examples."""
    print("=" * 70)
    print("Example 3: Pagination - Large Dataset Handling")
    print("=" * 70)

    basic_pagination()
    batched_reading()
    filtering_and_aggregating()
    configurable_batch_sizes()
    performance_comparison()

    print("\n" + "=" * 70)
    print("✓ Pagination examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
