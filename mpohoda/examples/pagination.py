"""
Example 3: Pagination - Handling Large Datasets

This example demonstrates two pagination strategies for handling large datasets:

1. Offset-Based Pagination - Traditional approach using page numbers
   - Good for: Small to medium datasets, UI navigation
   - Bad for: Large datasets, dynamic data

2. Keyset-Based Pagination - Using cursors (recommended)
   - Good for: Large datasets, efficient, no position skipping
   - Bad for: UI pagination with specific page numbers

Run with:
    export MPOHODA_API_KEY=your_api_key
    python examples/pagination.py
"""

from mpohoda import MPohodaDriver


def example_offset_based_pagination():
    """
    Offset-based pagination using PageNumber and PageSize.

    This is the traditional approach but less efficient for large datasets.
    """
    print("\n=== Offset-Based Pagination ===")
    print("Reading Activities using offset pagination (PageNumber + PageSize)")

    driver = MPohodaDriver.from_env()

    try:
        total_records = 0
        page_number = 1
        page_size = 50

        while True:
            print(f"\nFetching page {page_number} (size: {page_size})...")

            # Read specific page
            records = driver.read(
                "Activities",
                page_number=page_number,
                page_size=page_size
            )

            if not records:
                print(f"Page {page_number} is empty. Stopping.")
                break

            total_records += len(records)
            print(f"  ✓ Got {len(records)} records")

            # Process batch
            for i, record in enumerate(records[:3], 1):
                record_id = record.get("id", "N/A")
                description = record.get("description", "N/A")
                print(f"    {i}. {record_id}: {description[:50]}")

            if len(records) < page_size:
                print(f"Got {len(records)} records (less than page size), stopping.")
                break

            page_number += 1

            # Safety: Stop after 5 pages for demo
            if page_number > 5:
                print(f"Demo: Stopping after 5 pages")
                break

        print(f"\n✅ Total records processed: {total_records}")

    finally:
        driver.close()


def example_keyset_pagination():
    """
    Keyset-based pagination using After cursor (recommended).

    This is more efficient for large datasets and handles concurrent modifications better.
    """
    print("\n=== Keyset-Based Pagination (Recommended) ===")
    print("Reading Activities using keyset pagination (After cursor)")

    driver = MPohodaDriver.from_env()

    try:
        total_records = 0
        batch_number = 1
        batch_size = 50

        for batch in driver.read_batched("Activities", batch_size=batch_size):
            print(f"\nBatch {batch_number} (size: {batch_size}):")
            print(f"  ✓ Got {len(batch)} records")

            total_records += len(batch)

            # Process batch
            for i, record in enumerate(batch[:3], 1):
                record_id = record.get("id", "N/A")
                description = record.get("description", "N/A")
                print(f"    {i}. {record_id}: {description[:50]}")

            batch_number += 1

            # Safety: Stop after 5 batches for demo
            if batch_number > 5:
                print(f"\nDemo: Stopping after 5 batches")
                break

        print(f"\n✅ Total records processed: {total_records}")

    finally:
        driver.close()


def example_filtered_pagination():
    """
    Pagination with filtering (ModifiedSince).

    Filter results to only records modified after a certain date.
    """
    print("\n=== Filtered Pagination ===")
    print("Reading Activities modified after a specific date")

    driver = MPohodaDriver.from_env()

    try:
        filters = {
            "ModifiedSince": "2025-01-01"  # Only records modified after this date
        }

        print(f"\nFilters: {filters}")

        # Read with filters
        records = driver.read(
            "Activities",
            filters=filters,
            page_size=50,
            page_number=1
        )

        print(f"✓ Got {len(records)} modified records")

        # Process results
        for i, record in enumerate(records[:5], 1):
            record_id = record.get("id", "N/A")
            created = record.get("createdDate", "N/A")
            print(f"  {i}. {record_id} (Created: {created})")

        print(f"\n✅ Total: {len(records)} records")

    finally:
        driver.close()


def example_pagination_with_counting():
    """
    Pagination while counting total records and processing statistics.

    Demonstrates how to gather statistics while iterating.
    """
    print("\n=== Pagination with Statistics ===")
    print("Reading BusinessPartners and gathering statistics")

    driver = MPohodaDriver.from_env()

    try:
        total_records = 0
        total_batches = 0
        records_by_page = []

        for batch in driver.read_batched("BusinessPartners", batch_size=50):
            total_batches += 1
            batch_count = len(batch)
            total_records += batch_count
            records_by_page.append(batch_count)

            print(f"Batch {total_batches}: {batch_count} records")

            # Safety: Stop after 5 batches for demo
            if total_batches >= 5:
                print("Demo: Stopping after 5 batches")
                break

        # Print statistics
        print(f"\n--- Statistics ---")
        print(f"Total batches: {total_batches}")
        print(f"Total records: {total_records}")
        print(f"Average per batch: {total_records / total_batches:.1f}")
        print(f"Records per page:")
        for i, count in enumerate(records_by_page, 1):
            print(f"  Batch {i}: {count}")

    finally:
        driver.close()


def example_pagination_comparison():
    """
    Compare offset-based and keyset-based pagination.

    Shows pros and cons of each approach.
    """
    print("\n=== Pagination Methods Comparison ===")

    comparison = """
OFFSET-BASED PAGINATION (PageNumber + PageSize):
  Pros:
    ✓ Simple to understand
    ✓ Good for UI navigation
    ✓ Can jump to specific page
  Cons:
    ✗ Less efficient for large datasets
    ✗ Can miss/duplicate records if data changes during pagination
    ✗ Slower as offset increases

KEYSET-BASED PAGINATION (After cursor):
  Pros:
    ✓ Efficient for large datasets
    ✓ Handles concurrent modifications better
    ✓ No duplicate or missed records
    ✓ Consistent performance
  Cons:
    ✗ Cannot jump to arbitrary page
    ✗ Must go through pages in order

RECOMMENDATION:
  Use keyset-based (read_batched()) for:
    - Processing large datasets
    - Regular data exports
    - Background jobs
    - Guaranteed consistent results

  Use offset-based (read()) for:
    - Small datasets
    - UI pagination
    - When you need specific page numbers
"""
    print(comparison)


def main():
    """Run all pagination examples."""
    print("=" * 70)
    print("mPOHODA Driver Pagination Examples")
    print("=" * 70)

    # Example 1: Offset-based pagination
    example_offset_based_pagination()

    # Example 2: Keyset-based pagination (recommended)
    example_keyset_pagination()

    # Example 3: Filtered pagination
    example_filtered_pagination()

    # Example 4: Pagination with statistics
    example_pagination_with_counting()

    # Example 5: Comparison
    example_pagination_comparison()

    print("\n" + "=" * 70)
    print("✅ Pagination examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
