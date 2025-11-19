#!/usr/bin/env python3
"""
Example: Create and update records

This example demonstrates write operations: creating new records and updating existing ones.

Usage:
    export FIDOO_API_KEY="your_api_key_here"
    python create_and_update.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fidoo7 import Fidoo7Driver, ValidationError, ObjectNotFoundError


def example_create_cost_center():
    """Example: Create a cost center"""
    print("\n1. Creating Cost Center")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Check if write is supported
        capabilities = client.get_capabilities()
        if not capabilities.write:
            print("✗ API does not support write operations")
            return

        # Create new cost center
        new_cc = client.create("cost_center", {
            "name": "Engineering Department",
            "description": "All engineering-related expenses"
        })

        print(f"✓ Created cost center")
        print(f"  ID: {new_cc.get('id', new_cc.get('costCenterId', 'N/A'))}")
        print(f"  Name: {new_cc.get('name', 'N/A')}")

        return new_cc.get('id') or new_cc.get('costCenterId')

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()

    return None


def example_update_cost_center(cc_id):
    """Example: Update a cost center"""
    print("\n2. Updating Cost Center")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Update the cost center
        updated = client.update("cost_center", cc_id, {
            "description": "Engineering team - updated description"
        })

        print(f"✓ Updated cost center")
        print(f"  ID: {updated.get('id', updated.get('costCenterId', 'N/A'))}")
        print(f"  Name: {updated.get('name', 'N/A')}")

    except ObjectNotFoundError as e:
        print(f"✗ Cost center not found: {e}")
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()


def example_batch_create_projects():
    """Example: Create multiple projects in batch"""
    print("\n3. Batch Creating Projects")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    projects_data = [
        {"name": "Project Alpha", "description": "Q1 Initiative"},
        {"name": "Project Beta", "description": "Q2 Initiative"},
        {"name": "Project Gamma", "description": "Q3 Initiative"},
    ]

    created_projects = []

    try:
        for project_data in projects_data:
            project = client.create("project", project_data)
            created_projects.append(project)
            print(f"✓ Created: {project.get('name', 'N/A')}")

        print(f"\n✓ Successfully created {len(created_projects)} projects")

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()

    return created_projects


def example_safe_create_with_validation():
    """Example: Safe creation with field validation"""
    print("\n4. Safe Create with Validation")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # First, discover available fields
        fields = client.get_fields("cost_center")
        print(f"Available fields: {list(fields.keys())}")

        # Prepare data with known fields
        cc_data = {
            "name": "Sales Department",
            "description": "Sales team expenses"
        }

        # Create with safe field access
        new_cc = client.create("cost_center", cc_data)
        print(f"✓ Created cost center: {new_cc.get('name', 'N/A')}")

    except ValidationError as e:
        print(f"✗ Validation error: {e.message}")
        print(f"  Missing fields: {e.details.get('missing_fields', [])}")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()


def example_error_handling_create():
    """Example: Error handling during creation"""
    print("\n5. Error Handling During Creation")
    print("-" * 60)

    client = Fidoo7Driver.from_env()

    try:
        # Try to create with invalid object type
        result = client.create("invalid_object", {"name": "Test"})

    except ObjectNotFoundError as e:
        print(f"✗ Object type not supported: {e.message}")
        print(f"  Available types: {list(client.list_objects())}")

    except ValidationError as e:
        print(f"✗ Validation failed: {e.message}")
        print(f"  Details: {e.details}")

    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    finally:
        client.close()


def main():
    print("=" * 60)
    print("Fidoo7 Driver - Create and Update Examples")
    print("=" * 60)

    # Run examples
    cc_id = example_create_cost_center()

    if cc_id:
        example_update_cost_center(cc_id)

    example_batch_create_projects()
    example_safe_create_with_validation()
    example_error_handling_create()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
