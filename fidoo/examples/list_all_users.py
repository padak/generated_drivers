#!/usr/bin/env python3
"""
Example: List all users from Fidoo API

This example demonstrates basic read operations to retrieve and display user information.

Usage:
    export FIDOO_API_KEY="your_api_key_here"
    python list_all_users.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fidoo7 import Fidoo7Driver


def main():
    # Initialize client from environment
    client = Fidoo7Driver.from_env()

    try:
        print("Fetching all users from Fidoo...")
        print("-" * 60)

        # Query all users (with pagination limit)
        users = client.read("user/get-users", limit=100)

        if not users:
            print("No users found")
            return

        print(f"\nFound {len(users)} users:\n")

        # Display users
        for i, user in enumerate(users, 1):
            first_name = user.get("firstName", "N/A")
            last_name = user.get("lastName", "N/A")
            email = user.get("email", "N/A")
            state = user.get("userState", "N/A")

            print(f"{i}. {first_name} {last_name}")
            print(f"   Email: {email}")
            print(f"   State: {state}")
            print()

        print("-" * 60)
        print(f"Total: {len(users)} users")

    except Exception as e:
        print(f"Error: {e}")
        return 1

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
