"""
Example 4: Write Operations

Demonstrates create, update, and delete operations:
- Creating new resources
- Updating existing resources
- Deleting resources
- Error handling for write operations
- Validating before writing

This example shows how to perform write operations
on Stripe resources.
"""

from stripe_driver import StripeDriver, ValidationError, ObjectNotFoundError


def create_product():
    """Demonstrate creating a new product."""
    print("\n[1] Creating a Product")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        product_data = {
            "name": "Example Product",
            "type": "service",
            "description": "A test product created by the driver example",
        }

        print(f"  Creating product: {product_data['name']}...")
        product = client.create("products", product_data)

        print(f"  ✓ Product created successfully")
        print(f"    ID: {product.get('id')}")
        print(f"    Name: {product.get('name')}")
        print(f"    Type: {product.get('type')}")
        print(f"    Created at: {product.get('created')}")

        return product.get("id")

    except ValidationError as e:
        print(f"  ✗ Validation error: {e.message}")
        print(f"    Details: {e.details}")
        return None

    finally:
        client.close()


def update_product(product_id):
    """Demonstrate updating an existing product."""
    print("\n[2] Updating a Product")
    print("-" * 70)

    if not product_id:
        print("  Skipping: No product ID provided")
        return

    client = StripeDriver.from_env()

    try:
        update_data = {
            "name": "Updated Example Product",
            "description": "Updated description from driver example",
        }

        print(f"  Updating product {product_id}...")
        print(f"  New data: {update_data}")

        updated = client.update("products", product_id, update_data)

        print(f"  ✓ Product updated successfully")
        print(f"    Name: {updated.get('name')}")
        print(f"    Description: {updated.get('description')}")
        print(f"    Updated: {updated.get('updated')}")

    except ObjectNotFoundError as e:
        print(f"  ✗ Product not found: {e.message}")

    except ValidationError as e:
        print(f"  ✗ Validation error: {e.message}")

    finally:
        client.close()


def delete_resource(product_id):
    """Demonstrate deleting a resource."""
    print("\n[3] Deleting a Product")
    print("-" * 70)

    if not product_id:
        print("  Skipping: No product ID provided")
        return

    client = StripeDriver.from_env()

    try:
        print(f"  Deleting product {product_id}...")
        success = client.delete("products", product_id)

        if success:
            print(f"  ✓ Product deleted successfully")
        else:
            print(f"  ✗ Product deletion failed")

    except ObjectNotFoundError as e:
        print(f"  ✗ Product not found: {e.message}")

    finally:
        client.close()


def create_customer():
    """Demonstrate creating a customer."""
    print("\n[4] Creating a Customer")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        customer_data = {
            "email": "test@example.com",
            "name": "Test Customer",
            "description": "Created by driver example",
        }

        print(f"  Creating customer: {customer_data['name']}...")
        customer = client.create("customers", customer_data)

        print(f"  ✓ Customer created successfully")
        print(f"    ID: {customer.get('id')}")
        print(f"    Email: {customer.get('email')}")
        print(f"    Name: {customer.get('name')}")

        return customer.get("id")

    except ValidationError as e:
        print(f"  ✗ Validation error: {e.message}")
        return None

    finally:
        client.close()


def create_with_validation():
    """Demonstrate validation best practices."""
    print("\n[5] Create with Validation")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        # Example: Creating a product with all fields
        print("  Creating product with full validation...")

        product_data = {
            "name": "Premium Service",
            "type": "service",
            "description": "Premium service with full details",
            "metadata": {
                "tier": "premium",
                "created_by": "driver_example",
            },
        }

        print(f"  Data validation:")
        print(f"    ✓ Name: {product_data['name']} (required)")
        print(f"    ✓ Type: {product_data['type']} (required)")
        print(f"    ✓ Description: Provided")
        print(f"    ✓ Metadata: Included")

        product = client.create("products", product_data)
        print(f"  ✓ Product created with ID: {product.get('id')}")

    except ValidationError as e:
        print(f"  ✗ Validation failed:")
        print(f"    Message: {e.message}")
        if "missing_fields" in e.details:
            print(f"    Missing: {e.details['missing_fields']}")

    finally:
        client.close()


def batch_updates():
    """Demonstrate updating multiple resources."""
    print("\n[6] Batch Updates (Sequential)")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        # Note: Stripe API doesn't support true bulk updates
        # Each update is a separate API call

        print("  Fetching products to update...")
        products = client.read("products", limit=3)
        print(f"  ✓ Found {len(products)} products")

        update_count = 0
        for product in products:
            product_id = product.get("id")
            current_name = product.get("name", "Unnamed")

            try:
                # Update each product
                updated_product = client.update(
                    "products",
                    product_id,
                    {"description": f"Updated: {current_name}"},
                )
                update_count += 1
                print(f"  ✓ Updated: {product_id}")

            except Exception as e:
                print(f"  ✗ Failed to update {product_id}: {e}")

        print(f"\n  ✓ Successfully updated {update_count} of {len(products)} products")

    finally:
        client.close()


def error_recovery():
    """Demonstrate error recovery for write operations."""
    print("\n[7] Error Recovery for Write Operations")
    print("-" * 70)

    client = StripeDriver.from_env()

    try:
        print("  Scenario 1: Updating non-existent resource")
        try:
            client.update("products", "prod_nonexistent", {"name": "New"})
        except ObjectNotFoundError as e:
            print(f"    ✓ Caught error: {e.message}")

        print("\n  Scenario 2: Invalid product data")
        try:
            # Empty data might cause validation error
            invalid_data = {}
            product = client.create("products", invalid_data)
        except ValidationError as e:
            print(f"    ✓ Caught error: {e.message}")

    finally:
        client.close()


def main():
    """Run all write operation examples."""
    print("=" * 70)
    print("Example 4: Write Operations - Create, Update, Delete")
    print("=" * 70)

    # Create operations
    product_id = create_product()
    customer_id = create_customer()

    # Update operations
    if product_id:
        update_product(product_id)

    # Delete operations
    if product_id:
        delete_resource(product_id)

    # Advanced operations
    create_with_validation()
    batch_updates()
    error_recovery()

    print("\n" + "=" * 70)
    print("✓ Write operation examples completed")
    print("=" * 70)


if __name__ == "__main__":
    main()
