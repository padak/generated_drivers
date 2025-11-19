"""
Example 4: Write Operations - Creating Records

This example demonstrates how to create new records in mPOHODA.

Supported operations:
- CREATE: Add new records (POST method)

Not supported (API limitations):
- UPDATE: Modify existing records (returns 405 Method Not Allowed)
- DELETE: Remove records (returns 405 Method Not Allowed)

Run with:
    export MPOHODA_API_KEY=your_api_key
    python examples/write_operations.py
"""

from mpohoda import MPohodaDriver, ValidationError


def example_create_business_partner():
    """
    Create a new business partner.

    This demonstrates the most common write operation.
    """
    print("\n=== Creating Business Partner ===")

    driver = MPohodaDriver.from_env()

    try:
        # Prepare data
        partner_data = {
            "name": "Example Corporation Ltd",
            "taxNumber": "CZ87654321",
            "identificationNumber": "87654321",
            "addresses": [
                {
                    "type": "CONTACT",
                    "street": "Business Street 123",
                    "city": "Prague",
                    "postalCode": "11000",
                    "country": "CZ"
                }
            ]
        }

        print("Creating new business partner...")
        print(f"Name: {partner_data['name']}")
        print(f"Tax Number: {partner_data['taxNumber']}")

        # Create the record
        created_partner = driver.create("BusinessPartners", partner_data)

        print("\n✅ Business partner created successfully!")
        print(f"Partner ID: {created_partner.get('id', 'N/A')}")
        print(f"Name: {created_partner.get('name', 'N/A')}")
        print(f"Tax Number: {created_partner.get('taxNumber', 'N/A')}")

        return created_partner

    except ValidationError as e:
        print(f"❌ Validation error: {e.message}")
        print(f"Details: {e.details}")
        return None

    finally:
        driver.close()


def example_create_multiple_partners():
    """
    Create multiple business partners in sequence.

    Demonstrates batch creation pattern.
    """
    print("\n=== Creating Multiple Business Partners ===")

    driver = MPohodaDriver.from_env()

    try:
        # Define multiple partners to create
        partners_data = [
            {
                "name": "Tech Solutions Inc",
                "taxNumber": "CZ11111111",
                "identificationNumber": "11111111",
                "addresses": [{
                    "type": "CONTACT",
                    "street": "Tech Street 1",
                    "city": "Prague",
                    "postalCode": "11000",
                    "country": "CZ"
                }]
            },
            {
                "name": "Business Services Ltd",
                "taxNumber": "CZ22222222",
                "identificationNumber": "22222222",
                "addresses": [{
                    "type": "CONTACT",
                    "street": "Business Street 2",
                    "city": "Brno",
                    "postalCode": "61200",
                    "country": "CZ"
                }]
            },
            {
                "name": "Digital Agency s.r.o.",
                "taxNumber": "CZ33333333",
                "identificationNumber": "33333333",
                "addresses": [{
                    "type": "CONTACT",
                    "street": "Digital Street 3",
                    "city": "Ostrava",
                    "postalCode": "70200",
                    "country": "CZ"
                }]
            }
        ]

        created_partners = []
        successful = 0
        failed = 0

        for i, partner_data in enumerate(partners_data, 1):
            try:
                print(f"\n[{i}/{len(partners_data)}] Creating: {partner_data['name']}")

                created = driver.create("BusinessPartners", partner_data)
                created_partners.append(created)
                successful += 1

                print(f"  ✓ Created with ID: {created.get('id', 'N/A')}")

            except ValidationError as e:
                print(f"  ✗ Failed: {e.message}")
                failed += 1

        print(f"\n--- Summary ---")
        print(f"Successfully created: {successful}")
        print(f"Failed: {failed}")
        print(f"Total processed: {len(partners_data)}")

        return created_partners

    finally:
        driver.close()


def example_error_handling_on_create():
    """
    Demonstrate error handling for create operations.

    Shows how to handle validation errors gracefully.
    """
    print("\n=== Error Handling on Create ===")

    driver = MPohodaDriver.from_env()

    try:
        # Invalid data - missing required field
        invalid_data = {
            # Missing 'name' - likely required
            "taxNumber": "CZ99999999",
            # Missing 'identificationNumber'
            # Missing 'addresses'
        }

        print("Attempting to create partner with incomplete data...")
        created = driver.create("BusinessPartners", invalid_data)

    except ValidationError as e:
        print(f"❌ Validation failed: {e.message}")

        # Handle validation errors
        if "missing_fields" in e.details:
            print("\nMissing required fields:")
            for field in e.details["missing_fields"]:
                print(f"  - {field}")

        if "errors" in e.details:
            print("\nField errors:")
            for field, errors in e.details["errors"].items():
                for error in errors:
                    print(f"  - {field}: {error}")

        print(f"\nDetails: {e.details}")

    finally:
        driver.close()


def example_create_with_optional_fields():
    """
    Create a partner with various optional fields.

    Demonstrates different data structures.
    """
    print("\n=== Creating Partner with Optional Fields ===")

    driver = MPohodaDriver.from_env()

    try:
        partner_data = {
            "name": "Premium Company",
            "taxNumber": "CZ44444444",
            "identificationNumber": "44444444",
            "addresses": [
                {
                    "type": "CONTACT",
                    "street": "Main Street 100",
                    "city": "Prague",
                    "postalCode": "11000",
                    "country": "CZ"
                },
                {
                    "type": "DELIVERY",
                    "street": "Warehouse Street 50",
                    "city": "Kladno",
                    "postalCode": "27201",
                    "country": "CZ"
                }
            ],
            # Optional fields (if supported by API)
            "email": "info@premium.example.com",
            "phone": "+420 212 345 678",
        }

        print("Creating partner with multiple addresses and contact info...")
        print(f"Name: {partner_data['name']}")
        print(f"Addresses: {len(partner_data['addresses'])}")
        print(f"Email: {partner_data.get('email', 'Not provided')}")
        print(f"Phone: {partner_data.get('phone', 'Not provided')}")

        created = driver.create("BusinessPartners", partner_data)

        print("\n✅ Partner created!")
        print(f"ID: {created.get('id', 'N/A')}")
        print(f"Name: {created.get('name', 'N/A')}")

    finally:
        driver.close()


def example_write_operations_not_supported():
    """
    Demonstrate operations that are not supported.

    mPOHODA API doesn't support UPDATE or DELETE operations.
    """
    print("\n=== Unsupported Operations ===")

    driver = MPohodaDriver.from_env()

    try:
        capabilities = driver.get_capabilities()

        print("Available operations:")
        print(f"  ✓ CREATE (write): {capabilities.write}")
        print(f"  ✗ UPDATE (update): {capabilities.update}")
        print(f"  ✗ DELETE (delete): {capabilities.delete}")

        print("\n⚠️  UPDATE and DELETE operations are not supported!")
        print("    The API returns HTTP 405 (Method Not Allowed)")

        print("\nAlternatives:")
        print("  - For updates: Create a new record")
        print("  - For deletes: Archive or mark as inactive")
        print("  - Contact mPOHODA support for bulk operations")

    finally:
        driver.close()


def main():
    """Run all write operation examples."""
    print("=" * 70)
    print("mPOHODA Driver Write Operations Examples")
    print("=" * 70)

    # Example 1: Create single partner
    example_create_business_partner()

    # Example 2: Create multiple partners
    example_create_multiple_partners()

    # Example 3: Error handling
    example_error_handling_on_create()

    # Example 4: Create with optional fields
    example_create_with_optional_fields()

    # Example 5: Unsupported operations
    example_write_operations_not_supported()

    print("\n" + "=" * 70)
    print("✅ Write operations examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
