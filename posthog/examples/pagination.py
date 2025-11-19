#!/usr/bin/env python3
"""
Pagination Example

Demonstrates efficient handling of large datasets:
- Manual pagination with limit/offset
- Automatic batched reading for memory efficiency
- Progress tracking
- Large dataset processing patterns

This example shows how to process large amounts of data without
loading everything into memory at once.

Requirements:
    - POSTHOG_API_KEY environment variable set

Usage:
    python pagination.py
"""

from posthog_driver import PostHogDriver, RateLimitError
import time


def example_manual_pagination():
    """Demonstrate manual pagination using limit/offset."""
    print("\n" + "=" * 70)
    print("1. Manual Pagination (Limit/Offset)")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        page_size = 10
        page = 1
        total_fetched = 0
        max_pages = 3  # Limit to 3 pages for demo

        print(f"  Fetching dashboards with manual pagination (page_size={page_size})...\n")

        while page <= max_pages:
            offset = (page - 1) * page_size

            try:
                # Fetch one page
                dashboards = driver.read("/dashboards", limit=page_size, offset=offset)

                if not dashboards:
                    print(f"  Page {page}: No more data")
                    break

                print(f"  Page {page} (offset {offset}): {len(dashboards)} dashboards")

                for i, dashboard in enumerate(dashboards, 1):
                    print(f"    {i}. {dashboard.get('name', 'Unnamed')}")

                total_fetched += len(dashboards)
                page += 1

                # Small delay between requests (good practice)
                time.sleep(0.1)

            except RateLimitError as e:
                print(f"  ✗ Rate limited on page {page}")
                retry_after = e.details.get('retry_after', 60)
                print(f"    Waiting {retry_after} seconds before retry...")
                time.sleep(retry_after)
                # Retry this page
                continue

        print(f"\n  Total fetched: {total_fetched} dashboards")

    finally:
        driver.close()


def example_batched_reading():
    """Demonstrate efficient batched reading."""
    print("\n" + "=" * 70)
    print("2. Batched Reading (Memory Efficient)")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        batch_size = 100
        total_processed = 0
        batches = 0
        batch_times = []

        print(f"  Processing events with batched reading (batch_size={batch_size})...\n")

        for batch in driver.read_batched("/events", batch_size=batch_size):
            start_time = time.time()
            batches += 1

            # Process batch
            total_processed += len(batch)
            batch_duration = time.time() - start_time

            # Track timing
            batch_times.append(batch_duration)

            # Show progress
            print(f"  Batch {batches}: {len(batch)} events (processed in {batch_duration:.3f}s)")

            # Process first 3 batches only (for demo)
            if batches >= 3:
                print(f"  (Stopping after 3 batches for demo)")
                break

        if batch_times:
            avg_time = sum(batch_times) / len(batch_times)
            print(f"\n  Statistics:")
            print(f"    Total batches: {batches}")
            print(f"    Total events: {total_processed}")
            print(f"    Avg time per batch: {avg_time:.3f}s")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_batched_filtering_and_aggregation():
    """Demonstrate filtering and aggregating data during batch processing."""
    print("\n" + "=" * 70)
    print("3. Filtering and Aggregating During Batch Processing")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Processing events and tracking by event type...\n")

        event_counts = {}
        total_events = 0
        batches_processed = 0

        for batch in driver.read_batched("/events", batch_size=100):
            batches_processed += 1

            # Filter and aggregate
            for event in batch:
                event_type = event.get("event", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                total_events += 1

            print(f"  Processed batch {batches_processed}: {len(batch)} events")

            # Stop after 5 batches for demo
            if batches_processed >= 5:
                print(f"  (Stopping after 5 batches for demo)")
                break

        # Show results
        print(f"\n  Summary:")
        print(f"    Total events: {total_events}")
        print(f"    Total batches: {batches_processed}")
        print(f"    Event types found: {len(event_counts)}")

        if event_counts:
            print(f"\n  Top event types:")
            sorted_events = sorted(
                event_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for event_type, count in sorted_events[:5]:
                percentage = (count / total_events) * 100
                print(f"    - {event_type}: {count} ({percentage:.1f}%)")
            if len(sorted_events) > 5:
                print(f"    ... and {len(sorted_events) - 5} more event types")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_pagination_with_filtering():
    """Demonstrate pagination with filtering."""
    print("\n" + "=" * 70)
    print("4. Pagination with Filtering")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Reading dashboards and filtering by creation date...\n")

        page_size = 20
        offset = 0
        dashboards_created_recently = []
        total_checked = 0

        while True:
            try:
                dashboards = driver.read("/dashboards", limit=page_size, offset=offset)

                if not dashboards:
                    print(f"  No more dashboards")
                    break

                total_checked += len(dashboards)
                print(f"  Checking {len(dashboards)} dashboards...")

                # Filter: Keep dashboards (simulate filtering)
                for dashboard in dashboards:
                    dashboards_created_recently.append({
                        "id": dashboard.get("id"),
                        "name": dashboard.get("name"),
                        "created": dashboard.get("created_at"),
                    })

                # Process only first 2 pages for demo
                offset += page_size
                if offset >= (page_size * 2):
                    print(f"  (Stopping after 2 pages for demo)")
                    break

                time.sleep(0.1)  # Rate limit friendly

            except RateLimitError:
                print(f"  Rate limited, waiting...")
                time.sleep(60)

        print(f"\n  Results:")
        print(f"    Total dashboards checked: {total_checked}")
        print(f"    Dashboards kept: {len(dashboards_created_recently)}")
        if dashboards_created_recently:
            print(f"\n    Sample dashboards:")
            for i, dashboard in enumerate(dashboards_created_recently[:3], 1):
                print(f"      {i}. {dashboard['name']} (created: {dashboard['created']})")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def example_rate_limit_aware_pagination():
    """Demonstrate rate limit aware pagination with delays."""
    print("\n" + "=" * 70)
    print("5. Rate Limit Aware Pagination")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        batch_size = 50
        delay_between_requests = 0.5  # 500ms delay for rate limiting
        total_processed = 0
        requests_made = 0

        print(f"  Processing with rate limit awareness...")
        print(f"  - Batch size: {batch_size}")
        print(f"  - Delay between requests: {delay_between_requests}s\n")

        for batch in driver.read_batched("/events", batch_size=batch_size):
            requests_made += 1
            total_processed += len(batch)

            print(f"  Request {requests_made}: {len(batch)} events (total: {total_processed})")

            # Check rate limit status
            rate_limit = driver.get_rate_limit_status()
            if rate_limit["remaining"] is not None:
                print(f"    Rate limit status: {rate_limit['remaining']} remaining")

            # Stop after 3 requests for demo
            if requests_made >= 3:
                print(f"  (Stopping after 3 requests for demo)")
                break

            # Add delay between requests
            if requests_made < 3:
                print(f"    Waiting {delay_between_requests}s...")
                time.sleep(delay_between_requests)

        print(f"\n  Summary:")
        print(f"    Total requests: {requests_made}")
        print(f"    Total events: {total_processed}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    finally:
        driver.close()


def main():
    """Run all pagination examples."""
    print("=" * 70)
    print("PostHog Driver - Pagination Examples")
    print("=" * 70)

    try:
        # Run demonstrations in order
        example_manual_pagination()
        example_batched_reading()
        example_batched_filtering_and_aggregation()
        example_pagination_with_filtering()
        example_rate_limit_aware_pagination()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")

    print("\n" + "=" * 70)
    print("All pagination examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
