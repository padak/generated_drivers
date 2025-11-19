"""
Example 2: Create and update a partner record

This example demonstrates:
- Creating new records
- Updating existing records
- Handling validation errors
- Transaction-like behavior
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import ValidationError, ObjectNotFoundError


def main():
    """Create and update a partner."""

    client = OdooDriver.from_env()

    try:
        # Step 1: Create a new partner
        print("Creating new partner...")

        partner_data = {
            "name": "Acme Corporation",
            "email": "contact@acme.com",
            "phone": "+1-555-0123",
            "customer": True,
            "supplier": False,
        }

        new_partner = client.create("res.partner", partner_data)

        print(f"✓ Created partner: {new_partner['name']} (ID: {new_partner['id']})\n")

        # Step 2: Update the partner
        print(f"Updating partner {new_partner['id']}...")

        update_data = {
            "phone": "+1-555-9999",
            "fax": "+1-555-0124",
            "website": "https://acme.com",
        }

        client.update("res.partner", str(new_partner['id']), update_data)

        print("✓ Partner updated\n")

        # Step 3: Read the updated record
        print("Reading updated partner...")

        updated = client.read(
            f"[['id', '=', {new_partner['id']}]]",
            limit=1
        )

        if updated:
            partner = updated[0]
            print(f"  Name: {partner['name']}")
            print(f"  Email: {partner['email']}")
            print(f"  Phone: {partner['phone']}")
            print(f"  Website: {partner.get('website', 'N/A')}")
            print()

        # Step 4: Cleanup (optional)
        print(f"Deleting partner {new_partner['id']}...")
        client.delete("res.partner", str(new_partner['id']))
        print("✓ Partner deleted\n")

    except ValidationError as e:
        print(f"Validation error: {e.message}")
        print(f"Details: {e.details}")

    except ObjectNotFoundError as e:
        print(f"Not found: {e.message}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
