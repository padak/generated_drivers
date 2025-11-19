"""
Example 3: Pagination & Large Datasets

Demonstrates efficient handling of large datasets with pagination:
- Offset-based pagination with limit and offset
- Batch processing for memory efficiency
- Processing large datasets without loading everything into memory
- Rate limit awareness during pagination

Prerequisites:
    export APIFY_API_TOKEN="your_token_here"

Run:
    python examples/03_pagination.py
"""

from apify_driver import ApifyDriver, RateLimitError
import time


def example_simple_pagination():
    """Example: Simple pagination with limit and offset"""
    print("\n1. SIMPLE PAGINATION (limit + offset)")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Get first page
        print("Getting first 5 actors...")
        page1 = client.read("/actors", limit=5, offset=0)
        print(f"  Page 1: {len(page1)} actors")
        for actor in page1:
            print(f"    • {actor.get('name', 'Unknown')}")

        # Get second page
        print("\nGetting next 5 actors...")
        page2 = client.read("/actors", limit=5, offset=5)
        print(f"  Page 2: {len(page2)} actors")
        for actor in page2:
            print(f"    • {actor.get('name', 'Unknown')}")

        # Get third page
        print("\nGetting next 5 actors...")
        page3 = client.read("/actors", limit=5, offset=10)
        print(f"  Page 3: {len(page3)} actors")
        if not page3:
            print("  (No more data)")

    finally:
        client.close()


def example_batch_processing():
    """Example: Memory-efficient batch processing"""
    print("\n2. BATCH PROCESSING (read_batched)")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Processing actors in batches of 5...")
        total_processed = 0
        batch_count = 0

        # read_batched() yields batches instead of loading all at once
        for batch in client.read_batched("/actors", batch_size=5):
            batch_count += 1
            total_processed += len(batch)

            print(f"\nBatch {batch_count}: {len(batch)} actors")
            for actor in batch:
                print(f"  • {actor.get('name', 'Unknown')} (ID: {actor.get('id', 'N/A')})")

            # Small delay to be respectful to rate limits
            time.sleep(0.1)

            # For demo purposes, stop after 3 batches
            if batch_count >= 3:
                print(f"\n(Stopping after {batch_count} batches for demo)")
                break

        print(f"\nTotal processed: {total_processed} actors in {batch_count} batches")

    except RateLimitError as e:
        print(f"Rate limited: {e.message}")
        print(f"Retry after {e.details.get('retry_after')} seconds")

    finally:
        client.close()


def example_memory_efficiency():
    """Example: Memory efficiency comparison"""
    print("\n3. MEMORY EFFICIENCY COMPARISON")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Method 1: Load all at once (NOT recommended for large datasets)")
        print("-" * 70)

        # This loads everything into memory at once
        all_actors = client.read("/actors", limit=100)
        print(f"Loaded {len(all_actors)} actors")
        print("Warning: All data in memory at once!")
        print(f"Memory usage: High for large datasets")

        print("\nMethod 2: Process in batches (RECOMMENDED)")
        print("-" * 70)

        print("Processing 100 actors in 10-record batches...")
        total = 0
        max_batches = 5  # For demo

        for batch_num, batch in enumerate(client.read_batched("/actors", batch_size=10), 1):
            total += len(batch)
            print(f"  Batch {batch_num}: {len(batch)} actors (total: {total})")

            # Process batch here
            # Memory only holds current batch, not all data

            if batch_num >= max_batches:
                print(f"  (Demo: stopping after {max_batches} batches)")
                break

        print(f"\nBatch processing: Only current batch in memory!")
        print(f"Memory usage: Low, constant regardless of total data")

    finally:
        client.close()


def example_pagination_patterns():
    """Example: Common pagination patterns"""
    print("\n4. COMMON PAGINATION PATTERNS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        # Pattern 1: Iterate through all pages
        print("Pattern 1: Iterate through pages manually")
        print("-" * 70)

        page_size = 3
        offset = 0
        page_num = 1

        while True:
            print(f"Fetching page {page_num}...")
            page = client.read("/actors", limit=page_size, offset=offset)

            if not page:
                print("No more data")
                break

            print(f"  Page {page_num}: {len(page)} actors")
            for actor in page:
                print(f"    • {actor.get('name', 'Unknown')}")

            offset += page_size
            page_num += 1

            # Demo: stop after 3 pages
            if page_num > 3:
                print(f"(Demo: stopping after {page_num - 1} pages)")
                break

        # Pattern 2: Process with automatic batching
        print("\nPattern 2: Automatic batching (preferred)")
        print("-" * 70)

        processed = 0
        for batch in client.read_batched("/actors", batch_size=3):
            processed += len(batch)
            print(f"Processing batch of {len(batch)} actors (total: {processed})")

            # Demo: stop after 3 batches
            if processed >= 9:
                print(f"(Demo: stopping after {processed} records)")
                break

    finally:
        client.close()


def example_rate_limit_aware_pagination():
    """Example: Rate limit aware pagination"""
    print("\n5. RATE LIMIT AWARE PAGINATION")
    print("-" * 70)

    client = ApifyDriver.from_env(max_retries=3)

    try:
        print("Processing with rate limit awareness...")
        print(f"Configuration: max_retries=3, automatic backoff on HTTP 429")

        batch_size = 10
        processed = 0

        for batch in client.read_batched("/actors", batch_size=batch_size):
            processed += len(batch)
            print(f"Batch: {len(batch)} actors (total: {processed})")

            # Check rate limit status
            status = client.get_rate_limit_status()
            remaining = status.get('remaining')
            if remaining and remaining < 20:
                print(f"  ⚠️  Rate limit warning: {remaining} requests remaining")

            # Small delay between batches (optional)
            time.sleep(0.05)

            # Demo: stop after a few batches
            if processed >= 20:
                print(f"(Demo: stopping after {processed} records)")
                break

        print(f"✓ Completed with automatic rate limit handling")

    except RateLimitError as e:
        print(f"Rate limit exceeded: {e.message}")
        print(f"Implement backoff: wait {e.details.get('retry_after')} seconds")

    finally:
        client.close()


def example_finding_specific_items():
    """Example: Finding specific items through pagination"""
    print("\n6. FINDING SPECIFIC ITEMS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        search_term = "crawler"
        found_count = 0

        print(f"Searching for actors containing '{search_term}'...")

        for batch in client.read_batched("/actors", batch_size=10):
            for actor in batch:
                actor_name = actor.get("name", "").lower()
                if search_term.lower() in actor_name:
                    found_count += 1
                    print(f"  ✓ Found: {actor.get('name')} (ID: {actor.get('id')})")

            if found_count >= 3:
                print(f"(Demo: stopping after {found_count} matches)")
                break

        if found_count == 0:
            print(f"No actors found containing '{search_term}'")

    finally:
        client.close()


def main():
    """Run all pagination examples"""
    print("=" * 70)
    print("EXAMPLE 3: Pagination & Large Datasets")
    print("=" * 70)

    example_simple_pagination()
    example_batch_processing()
    example_memory_efficiency()
    example_pagination_patterns()
    example_rate_limit_aware_pagination()
    example_finding_specific_items()

    print("\n" + "=" * 70)
    print("✓ Pagination examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
