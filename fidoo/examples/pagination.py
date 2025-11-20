"""
Example: Pagination - Efficient Large Dataset Processing

This example demonstrates:
- Cursor-based pagination with offset tokens
- Memory-efficient batch processing
- Processing large datasets
- Progress tracking
- Combining results from multiple batches

Run:
    export FIDOO_API_KEY="your_api_key_here"
    python pagination.py
"""

from fidoo8 import Fidoo8Driver


def main():
    """Demonstrate pagination for large datasets"""

    client = Fidoo8Driver.from_env()

    try:
        print("=" * 70)
        print("PAGINATION EXAMPLE - Process Large Datasets Efficiently")
        print("=" * 70)

        # Example 1: Simple batched reading
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Simple Batch Processing")
        print("=" * 70)

        print("\nProcessing users in batches of 50...")
        total_users = 0
        batch_count = 0

        # read_batched automatically handles cursor pagination
        for batch in client.read_batched("User", batch_size=50):
            batch_count += 1
            total_users += len(batch)

            print(f"\nBatch {batch_count}: {len(batch)} users")
            print(f"Total so far: {total_users}")

            # Show first few users in batch
            for i, user in enumerate(batch[:3], 1):
                print(f"  {i}. {user.get('firstName')} {user.get('lastName')}")

            if len(batch) > 3:
                print(f"  ... and {len(batch) - 3} more")

            # Stop after a few batches for demo
            if batch_count >= 3:
                print("\n[Demo: stopping after 3 batches]")
                break

        print(f"\n✅ Processed {batch_count} batches ({total_users} total users)")

        # Example 2: Process specific object with pagination
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Process Expenses with Pagination")
        print("=" * 70)

        print("\nProcessing expenses (batches of 25)...")
        total_expenses = 0
        expense_states = {}

        for batch in client.read_batched("Expense", batch_size=25):
            total_expenses += len(batch)

            # Track expense states
            for expense in batch:
                state = expense.get("state", "unknown")
                expense_states[state] = expense_states.get(state, 0) + 1

            print(f"Batch: {len(batch)} expenses | Total: {total_expenses}")

            # Stop after 2 batches for demo
            if total_expenses >= 50:
                break

        print(f"\nExpense state distribution:")
        for state, count in sorted(expense_states.items()):
            print(f"  {state:<20} {count:3d}")

        # Example 3: Collect all results (simpler API)
        print("\n" + "=" * 70)
        print("EXAMPLE 3: Get All Results at Once")
        print("=" * 70)

        print("\nQuerying all cards (returns all records)...")
        cards = client.read("Card", limit=100)
        print(f"✅ Got {len(cards)} cards")

        # Group by type
        card_types = {}
        for card in cards:
            card_type = card.get("cardType", "unknown")
            card_types[card_type] = card_types.get(card_type, 0) + 1

        print(f"\nCard type distribution:")
        for card_type, count in card_types.items():
            print(f"  {card_type:<20} {count:3d}")

        # Example 4: Aggregation pattern
        print("\n" + "=" * 70)
        print("EXAMPLE 4: Aggregate Data from Multiple Batches")
        print("=" * 70)

        print("\nAggregating user statistics...")

        stats = {
            "total_users": 0,
            "active_users": 0,
            "deactivated_users": 0,
            "with_app_access": 0,
        }

        for batch in client.read_batched("User", batch_size=50):
            for user in batch:
                stats["total_users"] += 1

                if user.get("userState") == "active":
                    stats["active_users"] += 1

                if user.get("deactivated"):
                    stats["deactivated_users"] += 1

                if user.get("usesApplication"):
                    stats["with_app_access"] += 1

            # Stop after first batch for demo
            break

        print(f"\nUser Statistics:")
        for key, value in stats.items():
            print(f"  {key:<25} {value}")

        # Example 5: Performance comparison
        print("\n" + "=" * 70)
        print("EXAMPLE 5: Pagination Performance Tips")
        print("=" * 70)

        print("\nTips for efficient pagination:")
        print("""
1. Use read_batched() for large datasets
   - Memory efficient (processes one batch at a time)
   - Automatic cursor token handling
   - Recommended for > 1000 records

2. Choose appropriate batch size
   - Default: 50 (safe for most cases)
   - Small datasets: 50-100
   - Large datasets: 50-100 (don't exceed 100)
   - Memory-constrained: 10-25

3. Stop early if possible
   - Filter/process while iterating
   - Break loop when condition met
   - Don't fetch entire dataset if not needed

4. Aggregate while iterating
   - Don't store all records
   - Calculate aggregates during iteration
   - Reduces memory usage

5. Use cursor tokens correctly
   - Driver handles offsetToken automatically
   - When nextOffsetToken is None, iteration ends
   - No need to manage tokens manually
        """)

        print("=" * 70)
        print("✅ Pagination examples completed!")
        print("=" * 70)

    finally:
        client.close()


if __name__ == "__main__":
    main()
