#!/usr/bin/env python3
"""
Example: Process large dataset with pagination

This example demonstrates memory-efficient processing of large datasets
using the read_batched() method with cursor-based pagination.

Usage:
    export FIDOO_API_KEY="your_api_key_here"
    python pagination_large_dataset.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fidoo7 import Fidoo7Driver


def process_batch(batch, batch_number):
    """
    Process a batch of records.

    Args:
        batch: List of records
        batch_number: Batch number for tracking
    """
    print(f"\nBatch {batch_number}: {len(batch)} records")

    # Process first few items as example
    for item in batch[:3]:
        print(f"  - {item}")

    if len(batch) > 3:
        print(f"  ... and {len(batch) - 3} more")


def main():
    # Initialize client from environment
    client = Fidoo7Driver.from_env()

    try:
        print("Processing large dataset with pagination...")
        print("=" * 60)

        total_processed = 0
        batch_number = 0

        # Use batched reading for memory efficiency
        for batch in client.read_batched("user/get-users", batch_size=50):
            batch_number += 1
            total_processed += len(batch)

            # Process batch
            process_batch(batch, batch_number)

            print(f"Total processed so far: {total_processed}")

        print("=" * 60)
        print(f"\nProcessing complete!")
        print(f"Total batches: {batch_number}")
        print(f"Total records: {total_processed}")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
