"""
Example 1: List all users from Fidoo

This example demonstrates:
- Loading credentials from environment
- Querying users
- Processing results
- Proper error handling
- Resource cleanup
"""

from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import ObjectNotFoundError, RateLimitError


def main():
    """List all users from Fidoo"""

    # Initialize client from environment
    # Requires: FIDOO_API_KEY environment variable
    client = Fidoo8Driver.from_env()

    try:
        # Query all users
        print("Fetching users from Fidoo...")
        users = client.read("User", limit=100)

        print(f"\nFound {len(users)} users:\n")

        for i, user in enumerate(users, 1):
            print(f"{i}. {user.get('firstName')} {user.get('lastName')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Status: {user.get('userState')}")
            print(f"   Deactivated: {user.get('deactivated')}")
            print()

    except ObjectNotFoundError as e:
        print(f"Error: {e.message}")
        print(f"Available objects: {e.details.get('available')}")

    except RateLimitError as e:
        print(f"Rate limited! Retry after {e.details['retry_after']} seconds")

    finally:
        # Always cleanup
        client.close()


if __name__ == "__main__":
    main()
