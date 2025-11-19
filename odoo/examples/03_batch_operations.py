"""
Example 3: Batch operations - Create multiple records

This example demonstrates:
- Creating multiple records efficiently
- Tracking creation results
- Error handling for batch operations
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import ValidationError


def main():
    """Create multiple partner records in batch."""

    client = OdooDriver.from_env()

    try:
        # Define multiple companies to create
        companies = [
            {"name": "Company A", "customer": True, "supplier": False},
            {"name": "Company B", "customer": False, "supplier": True},
            {"name": "Company C", "customer": True, "supplier": True},
            {"name": "Company D", "customer": True, "supplier": False},
            {"name": "Company E", "customer": False, "supplier": True},
        ]

        print(f"Creating {len(companies)} partners...\n")

        created_ids = []
        for i, company_data in enumerate(companies, 1):
            try:
                record = client.create("res.partner", company_data)
                created_ids.append(record['id'])
                print(f"  [{i}/{len(companies)}] ✓ Created: {record['name']} (ID: {record['id']})")

            except ValidationError as e:
                print(f"  [{i}/{len(companies)}] ✗ Error: {e.message}")

        print(f"\nSuccessfully created {len(created_ids)} partners: {created_ids}\n")

        # Query the newly created records
        print("Verifying created records...")

        ids_str = ",".join(str(id) for id in created_ids)
        domain = f"[['id', 'in', [{ids_str}]]]"

        results = client.read(domain)
        print(f"✓ Found {len(results)} records in database\n")

        # Cleanup
        print("Cleaning up (deleting test records)...")
        for record_id in created_ids:
            client.delete("res.partner", str(record_id))
        print(f"✓ Deleted {len(created_ids)} test records\n")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
