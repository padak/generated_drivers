"""
Example: Advanced Usage - Complex Operations and Patterns

This example demonstrates:
- Multi-object queries and correlation
- Aggregations and analytics
- Complex filtering and processing
- Performance optimization
- Advanced error handling and recovery

Run:
    export FIDOO_API_KEY="your_api_key_here"
    python advanced_usage.py
"""

from collections import defaultdict
from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import RateLimitError, ConnectionError


def main():
    """Demonstrate advanced driver usage patterns"""

    client = Fidoo8Driver.from_env()

    try:
        print("=" * 70)
        print("ADVANCED USAGE EXAMPLE - Complex Operations")
        print("=" * 70)

        # Example 1: Multi-object analysis
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Multi-Object Analysis")
        print("=" * 70)

        print("\nAnalyzing relationship between users and cards...")

        # Get users
        users = client.read("User", limit=50)
        user_map = {u.get("userId"): u for u in users}
        print(f"  Loaded {len(users)} users")

        # Get cards
        cards = client.read("Card", limit=50)
        print(f"  Loaded {len(cards)} cards")

        # Analyze card distribution
        user_cards = defaultdict(list)
        for card in cards:
            owner_id = card.get("userId")
            if owner_id:
                user_cards[owner_id].append(card)

        print(f"\nCard ownership analysis:")
        print(f"  Users with cards: {len(user_cards)}")
        print(f"  Users without cards: {len(users) - len(user_cards)}")

        # Find users with most cards
        if user_cards:
            top_user = max(user_cards.items(), key=lambda x: len(x[1]))
            user_id, user_cards_list = top_user
            user = user_map.get(user_id)

            if user:
                print(f"\nTop card holder:")
                print(f"  {user.get('firstName')} {user.get('lastName')}")
                print(f"  Cards: {len(user_cards_list)}")

                for i, card in enumerate(user_cards_list[:3], 1):
                    print(f"    {i}. {card.get('embossName')} ({card.get('cardState')})")

        # Example 2: Time-series data aggregation
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Time-Series Analysis")
        print("=" * 70)

        print("\nAnalyzing expense trends...")

        expenses = client.read("Expense", limit=100)
        print(f"  Loaded {len(expenses)} expenses")

        # Group by state
        expenses_by_state = defaultdict(int)
        expenses_by_currency = defaultdict(int)
        total_amount_czk = 0

        for expense in expenses:
            state = expense.get("state", "unknown")
            currency = expense.get("currency", "CZK")
            amount = expense.get("amountCzk", 0)

            expenses_by_state[state] += 1
            expenses_by_currency[currency] += 1
            total_amount_czk += amount

        print(f"\nExpense Statistics:")
        print(f"  Total: {len(expenses)}")
        print(f"  Total Amount (CZK): {total_amount_czk:,.2f}")

        print(f"\nExpense by State:")
        for state, count in sorted(expenses_by_state.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(expenses)) * 100
            print(f"  {state:<20} {count:3d} ({percentage:5.1f}%)")

        print(f"\nExpense by Currency:")
        for currency, count in sorted(expenses_by_currency.items()):
            print(f"  {currency:<10} {count:3d}")

        # Example 3: Resilient data collection
        print("\n" + "=" * 70)
        print("EXAMPLE 3: Resilient Data Collection with Retry")
        print("=" * 70)

        print("\nCollecting data with fallback strategy...")

        # Try to get transactions with retry
        transactions = resilient_query(client, "Transaction", limit=25)
        print(f"✅ Collected {len(transactions)} transactions")

        # If failed, try alternative
        if len(transactions) == 0:
            print("ℹ️  Trying alternative endpoint...")
            transactions = resilient_query(client, "CardTransaction", limit=25)
            print(f"✅ Collected {len(transactions)} card transactions")

        # Example 4: Memory-efficient processing of large dataset
        print("\n" + "=" * 70)
        print("EXAMPLE 4: Memory-Efficient Large Dataset Processing")
        print("=" * 70)

        print("\nProcessing users with minimal memory usage...")

        stats = {
            "total": 0,
            "active": 0,
            "deactivated": 0,
            "with_app": 0,
            "kyc_ok": 0,
        }

        batch_count = 0
        for batch in client.read_batched("User", batch_size=50):
            batch_count += 1

            for user in batch:
                stats["total"] += 1
                if user.get("userState") == "active":
                    stats["active"] += 1
                if user.get("deactivated"):
                    stats["deactivated"] += 1
                if user.get("usesApplication"):
                    stats["with_app"] += 1
                if user.get("kycStatus") == "ok":
                    stats["kyc_ok"] += 1

            print(f"  Batch {batch_count}: Processed {len(batch)} users | Total: {stats['total']}")

            # Stop after reasonable amount
            if stats["total"] >= 200:
                break

        print(f"\nUser Statistics:")
        for key, value in stats.items():
            print(f"  {key:<20} {value}")

        # Example 5: Custom filtering and transformation
        print("\n" + "=" * 70)
        print("EXAMPLE 5: Custom Filtering and Transformation")
        print("=" * 70)

        print("\nFiltering and transforming card data...")

        # Get active cards only
        cards = client.read("Card", limit=50)
        active_cards = [c for c in cards if c.get("cardState") == "active"]
        print(f"  Found {len(active_cards)} active cards (of {len(cards)} total)")

        # Transform to custom format
        card_summary = [
            {
                "name": c.get("embossName"),
                "alias": c.get("alias"),
                "pan": c.get("maskedNumber"),
                "balance": c.get("availableBalance"),
                "status": c.get("cardState"),
            }
            for c in active_cards[:5]
        ]

        print(f"\nActive Cards Summary:")
        for card in card_summary:
            print(f"  {card['name']} ({card['alias']})")
            print(f"    PAN: {card['pan']}")
            print(f"    Balance: {card['balance']} CZK")
            print(f"    Status: {card['status']}")
            print()

        # Example 6: Performance monitoring
        print("=" * 70)
        print("EXAMPLE 6: Performance Monitoring")
        print("=" * 70)

        print("\nMonitoring query performance...")

        import time

        queries = [
            ("User", 50),
            ("Card", 50),
            ("Expense", 25),
            ("Transaction", 25),
        ]

        print(f"\nQuery Performance (first query only):")
        for obj_name, limit in queries:
            start = time.time()
            results = client.read(obj_name, limit=limit)
            duration = time.time() - start

            print(f"  {obj_name:<15} {len(results):3d} records in {duration*1000:.1f}ms")

        print("\n" + "=" * 70)
        print("✅ Advanced usage examples completed!")
        print("=" * 70)

    finally:
        client.close()


def resilient_query(client, object_name, limit=50, max_retries=3):
    """
    Query with comprehensive error handling and retry logic.

    Args:
        client: Fidoo8Driver instance
        object_name: Object to query
        limit: Records per request
        max_retries: Maximum retry attempts

    Returns:
        List of records (empty list on failure)
    """
    for attempt in range(max_retries):
        try:
            return client.read(object_name, limit=limit)

        except RateLimitError as e:
            if attempt < max_retries - 1:
                import time
                retry_after = e.details.get("retry_after", 60)
                print(f"  Rate limited. Waiting {retry_after}s before retry...")
                time.sleep(retry_after)
            else:
                print(f"  ❌ Rate limited (max retries reached)")
                return []

        except ConnectionError as e:
            if attempt < max_retries - 1:
                import time
                wait_time = 2 ** (attempt + 1)
                print(f"  Connection error. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Connection error (max retries reached)")
                return []

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []

    return []


if __name__ == "__main__":
    main()
