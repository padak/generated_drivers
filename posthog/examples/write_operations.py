#!/usr/bin/env python3
"""
Write Operations Example

Demonstrates CRUD operations:
- Create new resources
- Read existing resources
- Update existing resources
- Delete resources
- Batch create operations
- Error handling in write operations

This example shows how to modify data in PostHog using the driver.

Requirements:
    - POSTHOG_API_KEY environment variable set
    - API key must have write permissions

Usage:
    python write_operations.py
"""

from posthog_driver import (
    PostHogDriver,
    ValidationError,
    ObjectNotFoundError,
    DriverError,
)


def example_create_resource():
    """Demonstrate creating a new resource."""
    print("\n" + "=" * 70)
    print("1. Creating a New Resource (Dashboard)")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Create a new dashboard
        dashboard_data = {
            "name": "Demo Dashboard",
            "description": "Created by example script"
        }

        print(f"  Creating dashboard with data:")
        print(f"    Name: {dashboard_data['name']}")
        print(f"    Description: {dashboard_data['description']}")

        dashboard = driver.create("dashboards", dashboard_data)

        print(f"\n  ✓ Dashboard created successfully!")
        print(f"    ID: {dashboard.get('id')}")
        print(f"    Name: {dashboard.get('name')}")
        print(f"    Created: {dashboard.get('created_at')}")

        return dashboard.get('id')

    except ValidationError as e:
        print(f"  ✗ Validation Error: {e.message}")
        print(f"    Missing fields: {e.details.get('missing_fields')}")
        return None

    except DriverError as e:
        print(f"  ✗ Error creating dashboard: {e.message}")
        return None

    finally:
        driver.close()


def example_read_resource():
    """Demonstrate reading a resource."""
    print("\n" + "=" * 70)
    print("2. Reading Existing Resources")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        print("  Reading first 5 dashboards...")

        dashboards = driver.read("/dashboards", limit=5)

        print(f"\n  ✓ Found {len(dashboards)} dashboards:")
        for i, dashboard in enumerate(dashboards, 1):
            print(f"    {i}. {dashboard.get('name')} (ID: {dashboard.get('id')})")

        return dashboards[0].get('id') if dashboards else None

    except DriverError as e:
        print(f"  ✗ Error reading dashboards: {e.message}")
        return None

    finally:
        driver.close()


def example_update_resource(dashboard_id=None):
    """Demonstrate updating a resource."""
    print("\n" + "=" * 70)
    print("3. Updating an Existing Resource")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Get a dashboard to update
        if not dashboard_id:
            dashboards = driver.read("/dashboards", limit=1)
            if not dashboards:
                print("  ✗ No dashboards available to update")
                return False

            dashboard_id = dashboards[0].get('id')

        # Update the dashboard
        update_data = {
            "name": "Updated Dashboard Name",
            "description": "Updated by example script"
        }

        print(f"  Updating dashboard (ID: {dashboard_id})...")
        print(f"    New name: {update_data['name']}")
        print(f"    New description: {update_data['description']}")

        updated = driver.update("dashboards", dashboard_id, update_data)

        print(f"\n  ✓ Dashboard updated successfully!")
        print(f"    ID: {updated.get('id')}")
        print(f"    Name: {updated.get('name')}")
        print(f"    Updated: {updated.get('updated_at')}")

        return True

    except ObjectNotFoundError as e:
        print(f"  ✗ Dashboard not found: {e.message}")
        return False

    except ValidationError as e:
        print(f"  ✗ Validation Error: {e.message}")
        return False

    except DriverError as e:
        print(f"  ✗ Error updating dashboard: {e.message}")
        return False

    finally:
        driver.close()


def example_delete_resource(dashboard_id=None):
    """Demonstrate deleting a resource."""
    print("\n" + "=" * 70)
    print("4. Deleting a Resource (Soft Delete)")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Get a dashboard to delete (optional)
        if not dashboard_id:
            dashboards = driver.read("/dashboards", limit=1)
            if not dashboards:
                print("  ✗ No dashboards available to delete")
                return False

            dashboard_id = dashboards[0].get('id')

        print(f"  Deleting dashboard (ID: {dashboard_id})...")
        print(f"  Note: PostHog uses soft delete (resources are hidden, not removed)")

        success = driver.delete("dashboards", dashboard_id)

        if success:
            print(f"\n  ✓ Dashboard deleted successfully!")
        else:
            print(f"\n  ✗ Delete operation failed")

        return success

    except ObjectNotFoundError as e:
        print(f"  ✗ Dashboard not found: {e.message}")
        return False

    except DriverError as e:
        print(f"  ✗ Error deleting dashboard: {e.message}")
        return False

    finally:
        driver.close()


def example_batch_create():
    """Demonstrate creating multiple resources."""
    print("\n" + "=" * 70)
    print("5. Batch Create Operations")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Define multiple dashboards to create
        dashboards_to_create = [
            {"name": "Sales Dashboard", "description": "Sales metrics"},
            {"name": "Marketing Dashboard", "description": "Marketing KPIs"},
            {"name": "Analytics Dashboard", "description": "User analytics"},
        ]

        print(f"  Creating {len(dashboards_to_create)} dashboards in batch...\n")

        created = []
        failed = []

        for dashboard_data in dashboards_to_create:
            try:
                print(f"  Creating: {dashboard_data['name']}")
                dashboard = driver.create("dashboards", dashboard_data)
                created.append(dashboard)
                print(f"    ✓ Created with ID: {dashboard.get('id')}")

            except ValidationError as e:
                print(f"    ✗ Validation Error: {e.message}")
                failed.append((dashboard_data, str(e)))

            except DriverError as e:
                print(f"    ✗ Error: {e.message}")
                failed.append((dashboard_data, str(e)))

        print(f"\n  Summary:")
        print(f"    Successfully created: {len(created)}")
        print(f"    Failed: {len(failed)}")

        if created:
            print(f"\n  Created dashboards:")
            for dashboard in created:
                print(f"    - {dashboard.get('name')} (ID: {dashboard.get('id')})")

        return len(created) > 0

    finally:
        driver.close()


def example_crud_workflow():
    """Demonstrate complete CRUD workflow."""
    print("\n" + "=" * 70)
    print("6. Complete CRUD Workflow")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # CREATE
        print("\n  Step 1: CREATE")
        create_data = {
            "name": "Workflow Example Dashboard",
            "description": "Used for CRUD workflow demo"
        }
        dashboard = driver.create("dashboards", create_data)
        dashboard_id = dashboard.get('id')
        print(f"    ✓ Created dashboard: {dashboard_id}")

        # READ
        print(f"\n  Step 2: READ")
        dashboards = driver.read(f"/dashboards", limit=1)
        print(f"    ✓ Read {len(dashboards)} dashboard(s)")

        # UPDATE
        print(f"\n  Step 3: UPDATE")
        update_data = {
            "name": "Updated Workflow Example Dashboard",
            "description": "Updated description"
        }
        updated = driver.update("dashboards", dashboard_id, update_data)
        print(f"    ✓ Updated: {updated.get('name')}")

        # DELETE
        print(f"\n  Step 4: DELETE")
        success = driver.delete("dashboards", dashboard_id)
        print(f"    ✓ Deleted: {success}")

        print(f"\n  ✓ Complete CRUD workflow executed successfully!")

        return True

    except Exception as e:
        print(f"  ✗ Error in CRUD workflow: {e}")
        return False

    finally:
        driver.close()


def example_error_handling_in_writes():
    """Demonstrate error handling during write operations."""
    print("\n" + "=" * 70)
    print("7. Error Handling in Write Operations")
    print("=" * 70)

    driver = PostHogDriver.from_env()

    try:
        # Try to create with missing required field
        print("  Attempting to create dashboard without required field...")
        try:
            invalid_data = {
                "description": "Missing name field"
                # 'name' is missing!
            }
            dashboard = driver.create("dashboards", invalid_data)

        except ValidationError as e:
            print(f"    ✓ Validation Error Caught (expected!)")
            print(f"      Message: {e.message}")
            if "missing_fields" in e.details:
                print(f"      Missing: {e.details['missing_fields']}")

        # Try to update non-existent resource
        print(f"\n  Attempting to update non-existent dashboard...")
        try:
            updated = driver.update("dashboards", "nonexistent_id", {"name": "Updated"})

        except ObjectNotFoundError as e:
            print(f"    ✓ Object Not Found Error Caught (expected!)")
            print(f"      Message: {e.message}")

        # Try to delete non-existent resource
        print(f"\n  Attempting to delete non-existent dashboard...")
        try:
            success = driver.delete("dashboards", "nonexistent_id")

        except ObjectNotFoundError as e:
            print(f"    ✓ Object Not Found Error Caught (expected!)")
            print(f"      Message: {e.message}")

        print(f"\n  ✓ Error handling in write operations verified!")

        return True

    finally:
        driver.close()


def main():
    """Run all write operation examples."""
    print("=" * 70)
    print("PostHog Driver - Write Operations Examples")
    print("=" * 70)

    try:
        # Run demonstrations in order
        example_create_resource()
        dashboard_id = example_read_resource()

        if dashboard_id:
            example_update_resource(dashboard_id)
            example_delete_resource(dashboard_id)

        example_batch_create()
        example_crud_workflow()
        example_error_handling_in_writes()

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")

    print("\n" + "=" * 70)
    print("All write operation examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
