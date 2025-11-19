"""
Example 5: Pagination - Process large datasets efficiently

This example demonstrates:
- Using read_batched() for memory-efficient iteration
- Pagination with limit/offset
- Processing large result sets
- Progress tracking
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import ConnectionError


def main():
    """Process large dataset using pagination."""

    client = OdooDriver.from_env()

    try:
        # Step 1: Query all records using batched reading
        print("Processing large dataset with pagination...\n")

        domain = "[['active', '=', True]]"
        batch_size = 50
        total_processed = 0
        batch_count = 0

        print(f"Domain: {domain}")
        print(f"Batch size: {batch_size}\n")

        # Step 2: Iterate through batches
        for batch in client.read_batched(domain, batch_size=batch_size):
            batch_count += 1
            total_processed += len(batch)

            print(f"Batch {batch_count}:")
            print(f"  Records in batch: {len(batch)}")
            print(f"  Total processed: {total_processed}")

            # Process batch
            for record in batch:
                # In real scenario, do something with each record
                pass

            print()

        print(f"Processing complete!")
        print(f"  Total batches: {batch_count}")
        print(f"  Total records: {total_processed}\n")

        # Step 3: Manual pagination (for comparison)
        print("Manual pagination example:")

        limit = 100
        offset = 0
        page = 1

        while True:
            page_results = client.read(domain, limit=limit, offset=offset)

            print(f"  Page {page}: {len(page_results)} records")

            if len(page_results) < limit:
                # Last page (incomplete)
                break

            offset += limit
            page += 1

            if page > 5:
                # Limit to 5 pages for demo
                print("  ... (limited to 5 pages for demo)")
                break

        print()

    except ConnectionError as e:
        print(f"Connection error: {e.message}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
