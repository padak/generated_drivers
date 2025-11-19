"""
Example 1: Basic Usage

Demonstrates fundamental Stripe driver operations:
- Initialization from environment variables
- Simple queries (read operations)
- Result processing
- Resource cleanup

This example shows the most common use case: querying Stripe data.
"""

from stripe_driver import StripeDriver


def main():
    """
    Basic usage example demonstrating simple queries.

    Prerequisites:
        - Set STRIPE_API_KEY environment variable
        - Have active Stripe account with data
    """
    print("=" * 70)
    print("Example 1: Basic Usage - Querying Stripe Resources")
    print("=" * 70)

    # Initialize driver from environment
    # Best practice: Use environment variables for credentials
    print("\n[1] Initializing driver from environment...")
    client = StripeDriver.from_env()
    print("    ✓ Driver initialized")

    try:
        # Example 1.1: List all products
        print("\n[2] Querying products...")
        products = client.read("products", limit=5)
        print(f"    ✓ Found {len(products)} products (limited to 5)")

        if products:
            print("\n    Product Details:")
            for i, product in enumerate(products, 1):
                name = product.get("name", "N/A")
                product_id = product.get("id", "N/A")
                print(f"      {i}. {name} (ID: {product_id})")

        # Example 1.2: List customers
        print("\n[3] Querying customers...")
        customers = client.read("customers", limit=5)
        print(f"    ✓ Found {len(customers)} customers (limited to 5)")

        if customers:
            print("\n    Customer Details:")
            for i, customer in enumerate(customers, 1):
                email = customer.get("email", "N/A")
                customer_id = customer.get("id", "N/A")
                print(f"      {i}. {email} (ID: {customer_id})")

        # Example 1.3: List invoices
        print("\n[4] Querying invoices...")
        invoices = client.read("invoices", limit=5)
        print(f"    ✓ Found {len(invoices)} invoices (limited to 5)")

        if invoices:
            print("\n    Invoice Details:")
            for i, invoice in enumerate(invoices, 1):
                invoice_id = invoice.get("id", "N/A")
                status = invoice.get("status", "N/A")
                print(f"      {i}. Invoice {invoice_id} (Status: {status})")

        # Example 1.4: Check driver capabilities
        print("\n[5] Checking driver capabilities...")
        caps = client.get_capabilities()
        print(f"    ✓ Can read: {caps.read}")
        print(f"    ✓ Can write: {caps.write}")
        print(f"    ✓ Can update: {caps.update}")
        print(f"    ✓ Can delete: {caps.delete}")
        print(f"    ✓ Max page size: {caps.max_page_size}")

        # Example 1.5: List available resources
        print("\n[6] Available Stripe resources:")
        resources = client.list_objects()
        print(f"    ✓ {len(resources)} resource types available")
        print(f"    ✓ First 5: {', '.join(resources[:5])}")

    finally:
        # Always cleanup: close the connection
        print("\n[7] Cleanup...")
        client.close()
        print("    ✓ Driver closed")

    print("\n" + "=" * 70)
    print("✓ Example completed successfully")
    print("=" * 70)


if __name__ == "__main__":
    main()
