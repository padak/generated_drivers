"""
Example 2: Process large dataset with pagination

This example demonstrates:
- Memory-efficient batched reading
- Cursor-based pagination handling
- Processing large datasets
- Progress tracking
"""

from fidoo8 import Fidoo8Driver


def main():
    """Process users in batches using cursor-based pagination"""

    client = Fidoo8Driver.from_env()

    try:
        print("Processing users in batches...\n")

        total_processed = 0
        batch_count = 0

        # read_batched handles pagination automatically
        # Yields batches of records (memory-efficient)
        for batch in client.read_batched("User", batch_size=50):
            batch_count += 1
            batch_size = len(batch)
            total_processed += batch_size

            print(f"Batch {batch_count}: {batch_size} users")

            # Process each user in batch
            for user in batch:
                process_user(user)

            print(f"Total processed so far: {total_processed}\n")

        print(f"\nFinished!")
        print(f"Total batches: {batch_count}")
        print(f"Total users processed: {total_processed}")

    finally:
        client.close()


def process_user(user):
    """Process a single user record"""
    # Your processing logic here
    first_name = user.get('firstName', 'N/A')
    last_name = user.get('lastName', 'N/A')
    email = user.get('email', 'N/A')
    status = user.get('userState', 'N/A')

    # Example: print summary
    if user.get('deactivated'):
        status_marker = "[DEACTIVATED]"
    else:
        status_marker = ""

    print(f"  → {first_name} {last_name} ({email}) {status_marker}")


if __name__ == "__main__":
    main()
