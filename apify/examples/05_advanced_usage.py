"""
Example 5: Advanced Usage Patterns

Demonstrates advanced ApifyDriver usage patterns:
- Complex queries with multiple filters
- Searching and filtering results
- Data transformation
- Integration patterns
- Performance optimization
- Custom error handling

Prerequisites:
    export APIFY_API_TOKEN="your_token_here"

Run:
    python examples/05_advanced_usage.py
"""

import json
import time
from datetime import datetime
from apify_driver import ApifyDriver, RateLimitError, ObjectNotFoundError


def example_complex_queries():
    """Example: Complex queries with filtering"""
    print("\n1. COMPLEX QUERIES & FILTERING")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Retrieving and filtering actors...")

        # Get all actors
        all_actors = client.read("/actors", limit=20)
        print(f"Total actors retrieved: {len(all_actors)}")

        # Filter by name
        print("\nFilter: Actors with 'crawler' in name")
        crawler_actors = [a for a in all_actors if "crawler" in a.get("name", "").lower()]
        print(f"  Found: {len(crawler_actors)}")
        for actor in crawler_actors[:3]:
            print(f"    • {actor.get('name')} (ID: {actor.get('id')})")

        # Filter by public status
        print("\nFilter: Public actors")
        public_actors = [a for a in all_actors if a.get("isPublic")]
        print(f"  Found: {len(public_actors)}")

        # Sort by name
        print("\nSort: By name (alphabetically)")
        sorted_actors = sorted(all_actors, key=lambda a: a.get("name", "").lower())
        for actor in sorted_actors[:3]:
            print(f"    • {actor.get('name')}")

    finally:
        client.close()


def example_data_transformation():
    """Example: Transform and prepare data"""
    print("\n2. DATA TRANSFORMATION")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Retrieving and transforming actor data...")

        actors = client.read("/actors", limit=10)

        # Transform to simplified format
        simplified = [
            {
                "name": a.get("name"),
                "id": a.get("id"),
                "owner": a.get("username"),
                "visibility": "public" if a.get("isPublic") else "private",
                "created": a.get("createdAt"),
            }
            for a in actors
        ]

        print(f"\nTransformed {len(simplified)} actors to simplified format:")
        print(json.dumps(simplified[:2], indent=2))

        # Group by owner
        print("\nGrouping by owner...")
        by_owner = {}
        for actor in actors:
            owner = actor.get("username", "unknown")
            if owner not in by_owner:
                by_owner[owner] = []
            by_owner[owner].append(actor.get("name"))

        print(f"Found {len(by_owner)} owners:")
        for owner, actor_list in list(by_owner.items())[:3]:
            print(f"  • {owner}: {len(actor_list)} actors")

    finally:
        client.close()


def example_batch_statistics():
    """Example: Calculate statistics from batches"""
    print("\n3. BATCH STATISTICS")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Processing batches and calculating statistics...")

        stats = {
            "total_actors": 0,
            "total_batches": 0,
            "public_count": 0,
            "private_count": 0,
            "deprecated_count": 0,
            "batch_sizes": [],
        }

        batch_num = 0
        for batch in client.read_batched("/actors", batch_size=10):
            batch_num += 1
            batch_size = len(batch)
            stats["total_actors"] += batch_size
            stats["total_batches"] += 1
            stats["batch_sizes"].append(batch_size)

            for actor in batch:
                if actor.get("isPublic"):
                    stats["public_count"] += 1
                else:
                    stats["private_count"] += 1

                if actor.get("isDeprecated"):
                    stats["deprecated_count"] += 1

            print(f"  Batch {batch_num}: {batch_size} actors processed")

            # Demo: stop after 3 batches
            if batch_num >= 3:
                print(f"  (Demo: stopping after {batch_num} batches)")
                break

        print("\nStatistics:")
        print(f"  Total actors: {stats['total_actors']}")
        print(f"  Total batches: {stats['total_batches']}")
        print(f"  Public: {stats['public_count']}")
        print(f"  Private: {stats['private_count']}")
        print(f"  Deprecated: {stats['deprecated_count']}")
        print(f"  Average batch size: {sum(stats['batch_sizes']) / len(stats['batch_sizes']):.1f}")

    finally:
        client.close()


def example_performance_optimization():
    """Example: Optimize for performance"""
    print("\n4. PERFORMANCE OPTIMIZATION")
    print("-" * 70)

    print("Comparing different optimization strategies...\n")

    # Strategy 1: Small batches (many requests)
    print("Strategy 1: Small batches (limit=5)")
    print("-" * 70)
    client = ApifyDriver.from_env()
    try:
        start = time.time()
        count = 0
        for batch in client.read_batched("/actors", batch_size=5):
            count += len(batch)
            if count >= 20:
                break
        elapsed1 = time.time() - start
        print(f"Retrieved {count} actors in {elapsed1:.3f}s")
    finally:
        client.close()

    # Strategy 2: Large batches (fewer requests)
    print("\nStrategy 2: Large batches (limit=100)")
    print("-" * 70)
    client = ApifyDriver.from_env()
    try:
        start = time.time()
        all_data = client.read("/actors", limit=100)
        count = len(all_data)
        elapsed2 = time.time() - start
        print(f"Retrieved {count} actors in {elapsed2:.3f}s")
    finally:
        client.close()

    print("\nOptimization tips:")
    print("  • Use larger batch sizes for fewer requests (20-100)")
    print("  • Use smaller batches for faster response time")
    print("  • Add delays between batches to avoid rate limits")
    print("  • Use read_batched() for memory efficiency with large datasets")


def example_retry_strategy():
    """Example: Custom retry strategy"""
    print("\n5. RETRY STRATEGY")
    print("-" * 70)

    def retry_with_backoff(func, max_attempts=3, initial_delay=1):
        """Simple retry with exponential backoff"""
        delay = initial_delay
        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except RateLimitError as e:
                if attempt >= max_attempts:
                    raise

                wait_time = e.details.get('retry_after', delay)
                print(f"  Attempt {attempt} failed, retrying in {wait_time}s...")
                time.sleep(min(wait_time, delay))  # Don't exceed recommended delay
                delay *= 2

    client = ApifyDriver.from_env(max_retries=1)

    try:
        print("Using custom retry strategy...")

        def fetch_actors():
            return client.read("/actors", limit=5)

        result = retry_with_backoff(fetch_actors, max_attempts=3)
        print(f"✓ Successfully retrieved {len(result)} actors")

    except RateLimitError as e:
        print(f"Failed after retries: {e.message}")

    finally:
        client.close()


def example_error_recovery():
    """Example: Error recovery and fallback strategies"""
    print("\n6. ERROR RECOVERY & FALLBACK")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Attempting to fetch with fallbacks...\n")

        # Primary: Try to get /actors
        print("Primary: Fetching /actors")
        try:
            actors = client.read("/actors", limit=5)
            print(f"✓ Got {len(actors)} actors from /actors")

        except ObjectNotFoundError:
            print("✗ /actors endpoint not found")

            # Fallback: Try to get /runs
            print("\nFallback 1: Fetching /runs")
            try:
                runs = client.read("/runs", limit=5)
                print(f"✓ Got {len(runs)} runs")

            except ObjectNotFoundError:
                print("✗ /runs endpoint not found")

                # Fallback: List available resources
                print("\nFallback 2: Listing available resources")
                resources = client.list_objects()
                print(f"✓ Available resources: {resources}")

    finally:
        client.close()


def example_integration_pattern():
    """Example: Integration with external systems"""
    print("\n7. INTEGRATION PATTERN")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Simulating data synchronization...\n")

        print("Step 1: Fetch from Apify")
        actors = client.read("/actors", limit=5)
        print(f"  Retrieved {len(actors)} actors")

        print("\nStep 2: Transform for external system")
        external_data = []
        for actor in actors:
            external_data.append({
                "external_id": actor.get("id"),
                "name": actor.get("name"),
                "owner": actor.get("username"),
                "sync_timestamp": datetime.now().isoformat(),
                "source": "apify",
            })
        print(f"  Transformed {len(external_data)} records")

        print("\nStep 3: Prepare for import")
        print("  Sample record:")
        print(f"    {json.dumps(external_data[0], indent=6)}")

        print("\nStep 4: Send to external system (simulated)")
        print(f"  POST /api/sync with {len(external_data)} records")
        print("  ✓ Sync completed successfully")

    finally:
        client.close()


def example_field_mapping():
    """Example: Map fields between systems"""
    print("\n8. FIELD MAPPING")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Mapping Apify fields to external format...\n")

        # Get available fields
        fields = client.get_fields("actors")
        print(f"Apify Actor fields ({len(fields)}):")
        for field in list(fields.keys())[:5]:
            print(f"  • {field}")

        # Create mapping to external system
        print("\nField mapping to external system:")
        mapping = {
            "id": "actor_id",
            "name": "display_name",
            "username": "owner",
            "createdAt": "creation_date",
            "modifiedAt": "updated_date",
            "isPublic": "visibility",
        }

        for apify_field, external_field in mapping.items():
            print(f"  {apify_field:20} → {external_field}")

    finally:
        client.close()


def example_resource_monitoring():
    """Example: Monitor resource usage"""
    print("\n9. RESOURCE MONITORING")
    print("-" * 70)

    client = ApifyDriver.from_env()

    try:
        print("Monitoring Apify resource usage...\n")

        # Check rate limit
        status = client.get_rate_limit_status()
        print("Rate limit status:")
        print(f"  Remaining: {status.get('remaining', 'N/A')}")
        print(f"  Limit: {status.get('limit', 'N/A')}")
        print(f"  Reset: {status.get('reset_at', 'N/A')}")

        # Get capabilities
        capabilities = client.get_capabilities()
        print("\nDriver capabilities:")
        print(f"  Read: {capabilities.read}")
        print(f"  Write: {capabilities.write}")
        print(f"  Max page size: {capabilities.max_page_size}")

        # Estimate costs (simulated)
        print("\nEstimated usage (simulated):")
        print("  API calls this session: 3")
        print("  Remaining budget: 246,997/250,000")
        print("  % of monthly limit used: 0.001%")

    finally:
        client.close()


def main():
    """Run all advanced usage examples"""
    print("=" * 70)
    print("EXAMPLE 5: Advanced Usage Patterns")
    print("=" * 70)

    example_complex_queries()
    example_data_transformation()
    example_batch_statistics()
    example_performance_optimization()
    example_retry_strategy()
    example_error_recovery()
    example_integration_pattern()
    example_field_mapping()
    example_resource_monitoring()

    print("\n" + "=" * 70)
    print("✓ Advanced usage examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
