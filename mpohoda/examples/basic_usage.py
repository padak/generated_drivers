"""
Example 1: Basic Usage - Simple Read Operations

This example demonstrates the most common usage pattern:
1. Initialize the driver from environment variables
2. Read records from an object
3. Process the results
4. Cleanup

Run with:
    export MPOHODA_API_KEY=your_api_key
    python examples/basic_usage.py
"""

from mpohoda import MPohodaDriver


def main():
    """
    Basic usage example: Read activities from mPOHODA API.

    This demonstrates:
    - Initializing driver from environment
    - Discovering available objects
    - Reading records with pagination
    - Accessing record fields
    """

    # Initialize driver from environment variables
    # Reads: MPOHODA_API_KEY, MPOHODA_CLIENT_ID, MPOHODA_CLIENT_SECRET
    print("Initializing mPOHODA driver...")
    driver = MPohodaDriver.from_env()

    try:
        # Step 1: Discover available objects
        print("\n--- Available Objects ---")
        objects = driver.list_objects()
        print(f"Available objects ({len(objects)}):")
        for obj in objects:
            print(f"  - {obj}")

        # Step 2: Get capabilities (what the driver can do)
        print("\n--- Driver Capabilities ---")
        capabilities = driver.get_capabilities()
        print(f"Read operations:   {capabilities.read}")
        print(f"Write operations:  {capabilities.write}")
        print(f"Update operations: {capabilities.update}")
        print(f"Delete operations: {capabilities.delete}")
        print(f"Max page size:     {capabilities.max_page_size}")

        # Step 3: Read data from Activities object
        print("\n--- Reading Activities ---")
        activities = driver.read("Activities", page_size=50, page_number=1)
        print(f"Retrieved {len(activities)} activities")

        # Step 4: Display results
        if activities:
            print("\nFirst 5 activities:")
            for i, activity in enumerate(activities[:5], 1):
                # Display key fields (API may vary)
                activity_id = activity.get("id", "N/A")
                description = activity.get("description", "N/A")
                created_date = activity.get("createdDate", "N/A")

                print(f"  {i}. ID: {activity_id}")
                print(f"     Description: {description}")
                print(f"     Created: {created_date}")
        else:
            print("No activities found")

        # Step 5: Get field information for an object
        print("\n--- BusinessPartners Schema ---")
        fields = driver.get_fields("BusinessPartners")
        print(f"Available fields:")
        for field_name, field_info in list(fields.items())[:5]:
            field_type = field_info.get("type", "unknown")
            required = field_info.get("required", False)
            label = field_info.get("label", field_name)
            print(f"  - {field_name} ({field_type}) {'[REQUIRED]' if required else ''}")
            print(f"    Label: {label}")

        # Step 6: Read different object
        print("\n--- Reading Business Partners ---")
        partners = driver.read("BusinessPartners", page_size=10, page_number=1)
        print(f"Retrieved {len(partners)} business partners")

        if partners:
            print("\nFirst 3 partners:")
            for i, partner in enumerate(partners[:3], 1):
                partner_name = partner.get("name", "N/A")
                tax_number = partner.get("taxNumber", "N/A")
                print(f"  {i}. {partner_name} (Tax #: {tax_number})")

    finally:
        # Always cleanup
        print("\n--- Cleanup ---")
        driver.close()
        print("Driver closed successfully")


if __name__ == "__main__":
    main()
