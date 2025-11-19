"""
Example 4: Field discovery - Explore model schemas

This example demonstrates:
- Discovering available models
- Getting field definitions
- Checking field properties
- Building dynamic queries based on schema
"""

from odoo_driver import OdooDriver
from odoo_driver.exceptions import ObjectNotFoundError


def main():
    """Discover models and their fields."""

    client = OdooDriver.from_env()

    try:
        # Step 1: List all available models
        print("Discovering available models...\n")

        all_models = client.list_objects()
        print(f"Total models available: {len(all_models)}\n")

        # Show first 10 models
        print("Sample models:")
        for model in all_models[:10]:
            print(f"  - {model}")
        print()

        # Step 2: Explore a specific model (res.partner)
        model_name = "res.partner"
        print(f"Exploring model: {model_name}\n")

        fields = client.get_fields(model_name)

        print(f"Fields ({len(fields)} total):\n")

        # Categorize fields
        required_fields = []
        readonly_fields = []
        relation_fields = []

        for field_name, field_info in fields.items():
            print(f"  {field_name}:")
            print(f"    Type: {field_info['type']}")
            print(f"    Label: {field_info['label']}")
            print(f"    Required: {field_info['required']}")
            print(f"    ReadOnly: {field_info['readonly']}")
            if field_info.get('relation'):
                print(f"    Relation: {field_info['relation']}")
            print()

            # Categorize
            if field_info['required']:
                required_fields.append(field_name)
            if field_info['readonly']:
                readonly_fields.append(field_name)
            if field_info.get('relation'):
                relation_fields.append(field_name)

        # Step 3: Show summary
        print("Field Summary:")
        print(f"  Required fields ({len(required_fields)}): {', '.join(required_fields[:5])}")
        print(f"  Read-only fields ({len(readonly_fields)}): {', '.join(readonly_fields[:5])}")
        print(f"  Relation fields ({len(relation_fields)}): {', '.join(relation_fields)}")
        print()

        # Step 4: Build a query based on available fields
        print("Building query based on schema...")

        if 'active' in fields and fields['active']['type'] == 'boolean':
            if 'customer' in fields and fields['customer']['type'] == 'boolean':
                domain = "[['active', '=', True], ['customer', '=', True]]"
                print(f"Query: {domain}")

                partners = client.read(domain, limit=10)
                print(f"✓ Found {len(partners)} active customers\n")

    except ObjectNotFoundError as e:
        print(f"Model not found: {e.message}")
        print(f"Available models: {e.details.get('available', [])[:5]}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
