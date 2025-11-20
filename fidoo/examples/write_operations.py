"""
Example: Write Operations - Create, Update, Delete

This example demonstrates:
- Creating new records
- Updating existing records
- Deleting records
- Handling validation errors
- Verifying results

Run:
    export FIDOO_API_KEY="your_api_key_here"
    python write_operations.py

WARNING: This example modifies data!
         Use with caution on production systems.
         Consider using demo/test API first.
"""

from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import ValidationError, ObjectNotFoundError


def main():
    """Demonstrate write operations"""

    client = Fidoo8Driver.from_env()

    try:
        print("=" * 70)
        print("WRITE OPERATIONS EXAMPLE - Create, Update, Delete")
        print("=" * 70)

        # Example 1: Create a new user
        print("\n" + "=" * 70)
        print("EXAMPLE 1: Create a New User")
        print("=" * 70)

        print("\nCreating new user...")
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phone": "+420123456789",
            "employeeNumber": "EMP001",
        }

        print(f"User data: {user_data}")

        try:
            new_user = client.create("User", user_data)

            print(f"\n✅ User created successfully!")
            print(f"   User ID: {new_user.get('userId')}")
            print(f"   Name: {new_user.get('firstName')} {new_user.get('lastName')}")
            print(f"   Email: {new_user.get('email')}")

        except ValidationError as e:
            print(f"\n❌ Validation error: {e.message}")
            print(f"   Details: {e.details}")

        except Exception as e:
            print(f"\n❌ Error creating user: {e}")

        # Example 2: Update an expense
        print("\n" + "=" * 70)
        print("EXAMPLE 2: Update an Expense")
        print("=" * 70)

        print("\nFetching an expense to update...")
        expenses = client.read("Expense", limit=1)

        if expenses:
            expense = expenses[0]
            expense_id = expense.get("expenseId")

            print(f"Found expense: {expense.get('name')}")
            print(f"Current state: {expense.get('state')}")

            # Update the expense
            print(f"\nUpdating expense...")
            update_data = {
                "name": f"{expense.get('name')} [UPDATED]",
                "state": "approve",  # Change state to approve
            }

            try:
                updated = client.update("Expense", expense_id, update_data)

                print(f"\n✅ Expense updated successfully!")
                print(f"   New name: {updated.get('name')}")
                print(f"   New state: {updated.get('state')}")

            except ValidationError as e:
                print(f"\n❌ Validation error: {e.message}")

            except Exception as e:
                print(f"\n❌ Error updating expense: {e}")

        else:
            print("ℹ️  No expenses found to update")

        # Example 3: Delete a user (if supported)
        print("\n" + "=" * 70)
        print("EXAMPLE 3: Delete a User")
        print("=" * 70)

        print("\nNote: Delete operations should be used with caution!")
        print("      This example demonstrates the API, but doesn't actually")
        print("      delete anything for safety.")

        print("\nDelete capability check:")
        caps = client.get_capabilities()
        if caps.delete:
            print(f"✅ Driver supports delete operations")

            # Example: how you would delete
            print(f"\nHow to delete a user:")
            print(f"  user_id = 'some_user_id'")
            print(f"  success = client.delete('User', user_id)")

        else:
            print(f"❌ Driver does not support delete operations")

        # Example 4: Batch data creation pattern
        print("\n" + "=" * 70)
        print("EXAMPLE 4: Batch Creation Pattern")
        print("=" * 70)

        print("\nDemonstrating batch creation pattern...")

        users_to_create = [
            {
                "firstName": "Alice",
                "lastName": "Smith",
                "email": "alice.smith@example.com",
                "employeeNumber": "EMP002",
            },
            {
                "firstName": "Bob",
                "lastName": "Johnson",
                "email": "bob.johnson@example.com",
                "employeeNumber": "EMP003",
            },
            {
                "firstName": "Carol",
                "lastName": "Williams",
                "email": "carol.williams@example.com",
                "employeeNumber": "EMP004",
            },
        ]

        print(f"\nCreating {len(users_to_create)} users...")

        created_count = 0
        failed_count = 0
        created_users = []

        for user_data in users_to_create:
            try:
                print(f"\n  Creating: {user_data['firstName']} {user_data['lastName']}")
                new_user = client.create("User", user_data)
                print(f"    ✅ Created (ID: {new_user.get('userId')})")
                created_users.append(new_user)
                created_count += 1

            except ValidationError as e:
                print(f"    ❌ Validation error: {e.message}")
                failed_count += 1

            except Exception as e:
                print(f"    ❌ Error: {e}")
                failed_count += 1

        print(f"\n✅ Batch creation result:")
        print(f"   Created: {created_count}")
        print(f"   Failed: {failed_count}")

        # Example 5: Verify write operations
        print("\n" + "=" * 70)
        print("EXAMPLE 5: Verify Write Operations")
        print("=" * 70)

        print("\nRead operations are used to verify writes:")

        print("\n1. Get all users (verify creation):")
        users = client.read("User", limit=10)
        print(f"   ✅ Total users: {len(users)}")

        print("\n2. Get expenses (verify updates):")
        expenses = client.read("Expense", limit=10)
        print(f"   ✅ Total expenses: {len(expenses)}")

        print("\n3. Get cards (other object):")
        cards = client.read("Card", limit=10)
        print(f"   ✅ Total cards: {len(cards)}")

        print("\n" + "=" * 70)
        print("✅ Write operations examples completed!")
        print("=" * 70)

        print("\nBest Practices for Write Operations:")
        print("""
1. Validate data before creating/updating
   - Check required fields are present
   - Validate data types and formats
   - Handle validation errors gracefully

2. Always verify results after write
   - Query the record after creation
   - Confirm all fields were set correctly
   - Check related records if applicable

3. Handle errors appropriately
   - Catch ValidationError for data issues
   - Catch ConnectionError for transient failures
   - Implement retry logic for transient errors

4. Use transactions if available
   - Batch related operations together
   - Ensure consistency across multiple records
   - Rollback on error

5. Log all write operations
   - Record what was created/updated
   - Log timestamps and user info
   - Maintain audit trail for compliance
        """)

    finally:
        client.close()


if __name__ == "__main__":
    main()
