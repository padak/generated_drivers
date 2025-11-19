#!/usr/bin/env python3
"""
Example 4: User Properties Management

Demonstrates user property operations:
- Update user properties
- Use property operations ($set, $add, $append, etc.)
- Set once (only if not already set)
- Increment counters
- Add to arrays
- Remove properties

Run this example:
    export AMPLITUDE_API_KEY="your_api_key"
    python 4_user_properties.py
"""

import time
from amplitude import AmplitudeDriver


def example_simple_set():
    """Example: Simple property set."""
    print("\n" + "=" * 70)
    print("Example: Simple Property Set")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_example_001"
        print(f"Updating user properties for: {user_id}")

        driver.update("users", user_id, {
            "user_properties": {
                "$set": {
                    "plan": "premium",
                    "name": "John Doe",
                    "email": "john@example.com"
                }
            }
        })

        print("✓ User properties updated successfully")

    finally:
        driver.close()


def example_property_operations():
    """Example: Various property operations."""
    print("\n" + "=" * 70)
    print("Example: Property Operations")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_operations_001"
        print(f"Applying multiple property operations for: {user_id}")

        driver.update("users", user_id, {
            "user_properties": {
                # Set property value
                "$set": {
                    "plan": "enterprise",
                    "last_login": f"{time.time()}",
                    "status": "active"
                },
                # Set only if not already set
                "$setOnce": {
                    "signup_date": "2024-01-15",
                    "referral_source": "google"
                },
                # Increment numeric value
                "$add": {
                    "login_count": 1,
                    "credits": 50
                },
                # Append to array/list
                "$append": {
                    "interests": "machine-learning"
                },
                # Prepend to array/list
                "$prepend": {
                    "recent_actions": "viewed_pricing"
                }
            }
        })

        print("✓ Multiple property operations applied successfully")

    finally:
        driver.close()


def example_advanced_operations():
    """Example: Advanced array operations."""
    print("\n" + "=" * 70)
    print("Example: Advanced Array Operations")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_arrays_001"
        print(f"Managing array properties for: {user_id}")

        driver.update("users", user_id, {
            "user_properties": {
                # Initialize arrays
                "$set": {
                    "tags": ["new_user", "beta_tester"],
                    "preferences": ["email_notifications", "dark_mode"],
                    "view_count": 0
                },
                # Add to arrays
                "$append": {
                    "tags": "premium",
                    "preferences": "monthly_digest"
                },
                # Add to beginning of arrays
                "$prepend": {
                    "tags": "paying_customer"
                },
                # Increment counter
                "$add": {
                    "view_count": 5
                }
            }
        })

        print("✓ Array properties managed successfully")

    finally:
        driver.close()


def example_set_once():
    """Example: Set properties only if not already set."""
    print("\n" + "=" * 70)
    print("Example: Set Once (Initial Properties)")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_setonce_001"
        print(f"Setting initial properties for: {user_id}")

        driver.update("users", user_id, {
            "user_properties": {
                # These will only be set if not already present
                "$setOnce": {
                    "first_seen": "2024-11-19",
                    "signup_date": "2024-11-19",
                    "initial_source": "organic_search",
                    "initial_plan": "free"
                }
            }
        })

        print("✓ Initial properties set (if not already present)")

    finally:
        driver.close()


def example_increment_counters():
    """Example: Increment counters."""
    print("\n" + "=" * 70)
    print("Example: Increment Counters")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_counters_001"
        print(f"Incrementing user metrics for: {user_id}")

        driver.update("users", user_id, {
            "user_properties": {
                "$set": {
                    "total_purchases": 5,
                    "total_spent": 299.99,
                    "sessions": 42
                },
                "$add": {
                    "total_purchases": 1,
                    "total_spent": 49.99,
                    "sessions": 1
                }
            }
        })

        print("✓ Counters incremented successfully")

    finally:
        driver.close()


def example_complex_scenario():
    """Example: Complex real-world scenario."""
    print("\n" + "=" * 70)
    print("Example: Complex Real-World Scenario")
    print("=" * 70)

    print("Scenario: User signs up and purchases premium plan")

    try:
        driver = AmplitudeDriver.from_env()

        user_id = "user_complex_001"

        # Step 1: Set initial properties on signup
        print("\n1. Setting initial signup properties...")
        driver.update("users", user_id, {
            "user_properties": {
                "$setOnce": {
                    "signup_date": "2024-11-19",
                    "signup_source": "referral"
                },
                "$set": {
                    "status": "active"
                }
            }
        })

        # Step 2: Update after purchase
        print("2. Updating after purchase...")
        driver.update("users", user_id, {
            "user_properties": {
                "$set": {
                    "plan": "premium",
                    "last_purchase_date": "2024-11-19",
                    "last_purchase_amount": 99.99
                },
                "$add": {
                    "total_purchases": 1,
                    "total_revenue": 99.99,
                    "purchase_count": 1
                },
                "$append": {
                    "purchase_history": "premium_annual",
                    "user_tags": "paying_customer"
                }
            }
        })

        print("✓ Complex scenario completed successfully")

    finally:
        driver.close()


def example_user_segmentation():
    """Example: User segmentation via properties."""
    print("\n" + "=" * 70)
    print("Example: User Segmentation")
    print("=" * 70)

    try:
        driver = AmplitudeDriver.from_env()

        # User 1: Trial user
        print("\n1. Setting up trial user...")
        driver.update("users", "user_trial_001", {
            "user_properties": {
                "$set": {
                    "segment": "trial",
                    "plan": "free",
                    "trial_expiry": "2024-12-19"
                },
                "$setOnce": {
                    "signup_date": "2024-11-19"
                }
            }
        })

        # User 2: Premium user
        print("2. Setting up premium user...")
        driver.update("users", "user_premium_001", {
            "user_properties": {
                "$set": {
                    "segment": "premium",
                    "plan": "premium",
                    "auto_renewal": True
                },
                "$add": {
                    "premium_months": 1
                }
            }
        })

        # User 3: Enterprise user
        print("3. Setting up enterprise user...")
        driver.update("users", "user_enterprise_001", {
            "user_properties": {
                "$set": {
                    "segment": "enterprise",
                    "plan": "enterprise",
                    "account_manager": "john@company.com"
                },
                "$append": {
                    "team_members": "alice@company.com"
                }
            }
        })

        print("✓ User segmentation completed")

    finally:
        driver.close()


def main():
    """Run all user property examples."""
    print("=" * 70)
    print("Amplitude Driver - User Properties Examples")
    print("=" * 70)

    # Run examples
    example_simple_set()
    example_property_operations()
    example_advanced_operations()
    example_set_once()
    example_increment_counters()
    example_complex_scenario()
    example_user_segmentation()

    print("\n" + "=" * 70)
    print("User properties examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
