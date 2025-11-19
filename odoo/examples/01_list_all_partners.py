"""
Example 1: List all active partners from Odoo

This example demonstrates:
- Loading credentials from environment
- Querying with domain language
- Iterating through results
- Error handling
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import AuthenticationError, ConnectionError


def main():
    """List all active partners."""

    # Initialize client from environment variables
    try:
        client = OdooDriver.from_env()
    except AuthenticationError as e:
        print(f"Error: {e.message}")
        print(f"Required environment variables: {e.details['required_env_vars']}")
        return

    try:
        # Query all active partners using domain language
        # Domain: [['active', '=', True]]
        domain = "[['active', '=', True]]"

        partners = client.read(domain, limit=100)

        print(f"Found {len(partners)} active partners:\n")

        for partner in partners:
            print(f"  ID: {partner['id']}")
            print(f"  Name: {partner.get('name', 'N/A')}")
            print(f"  Email: {partner.get('email', 'N/A')}")
            print(f"  Phone: {partner.get('phone', 'N/A')}")
            print(f"  Is Customer: {partner.get('customer', False)}")
            print(f"  Is Supplier: {partner.get('supplier', False)}")
            print()

    except ConnectionError as e:
        print(f"Connection error: {e.message}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
