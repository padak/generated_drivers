"""
Example 5: Advanced Usage - Complex Patterns and Production Scenarios

This example demonstrates advanced patterns for production use:

1. Multi-object data synchronization
2. Retry and resilience patterns
3. Data transformation pipelines
4. Comprehensive logging and monitoring
5. Configuration management

Run with:
    export MPOHODA_API_KEY=your_api_key
    python examples/advanced_usage.py
"""

import logging
import json
from typing import List, Dict, Any
from datetime import datetime

from mpohoda import (
    MPohodaDriver,
    RateLimitError,
    AuthenticationError,
    ObjectNotFoundError,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MPohodaSync:
    """
    Advanced synchronization client for mPOHODA data.

    Features:
    - Multi-object data retrieval
    - Resilience and retry logic
    - Data transformation
    - Progress tracking
    - Detailed logging
    """

    def __init__(self, debug: bool = False):
        """Initialize the sync client."""
        self.driver = MPohodaDriver.from_env(debug=debug)
        self.debug = debug
        self.stats = {
            "objects_processed": 0,
            "records_processed": 0,
            "batches_processed": 0,
            "errors": 0,
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.driver.close()

    def get_object_count(self) -> Dict[str, int]:
        """
        Get count of records in each object.

        Returns:
            Dictionary mapping object names to record counts
        """
        logger.info("Fetching object record counts...")
        counts = {}

        for obj_name in self.driver.list_objects():
            try:
                # Get first page to see total count
                records = self.driver.read(obj_name, page_size=1)
                # In real API, would use totalItemCount from response
                counts[obj_name] = len(records)
                logger.info(f"  {obj_name}: ~{counts[obj_name]} records")
            except Exception as e:
                logger.warning(f"Failed to count {obj_name}: {e}")
                counts[obj_name] = 0

        return counts

    def sync_object(self, object_name: str) -> List[Dict[str, Any]]:
        """
        Synchronize all records from an object.

        Features:
        - Automatic pagination
        - Progress tracking
        - Error handling
        """
        logger.info(f"\nSynchronizing object: {object_name}")

        all_records = []
        batch_count = 0
        total_records = 0

        try:
            for batch in self.driver.read_batched(object_name, batch_size=50):
                batch_count += 1
                batch_size = len(batch)
                total_records += batch_size

                all_records.extend(batch)

                logger.debug(
                    f"  Batch {batch_count}: {batch_size} records "
                    f"(total: {total_records})"
                )

                # Stop after 5 batches for demo
                if batch_count >= 5:
                    logger.info("  (Demo: stopping after 5 batches)")
                    break

        except RateLimitError as e:
            logger.error(f"Rate limit hit: {e.message}")
            self.stats["errors"] += 1
            return all_records

        except Exception as e:
            logger.error(f"Error syncing {object_name}: {e}")
            self.stats["errors"] += 1
            return all_records

        self.stats["objects_processed"] += 1
        self.stats["records_processed"] += total_records
        self.stats["batches_processed"] += batch_count

        logger.info(
            f"  ✓ Synced {object_name}: {total_records} records "
            f"in {batch_count} batches"
        )

        return all_records

    def export_to_json(self, records: List[Dict[str, Any]], filename: str):
        """Export records to JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump(records, f, indent=2, default=str)
            logger.info(f"  ✓ Exported to {filename}")
        except Exception as e:
            logger.error(f"Failed to export: {e}")

    def transform_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform records for processing.

        Example: Flatten nested structures, add computed fields, etc.
        """
        transformed = []

        for record in records:
            transformed_record = {
                "id": record.get("id"),
                "created_at": record.get("createdDate"),
                "export_timestamp": datetime.now().isoformat(),
            }

            # Add other fields
            for key, value in record.items():
                if key not in transformed_record:
                    transformed_record[key] = value

            transformed.append(transformed_record)

        return transformed

    def print_stats(self):
        """Print synchronization statistics."""
        print("\n" + "=" * 60)
        print("Synchronization Statistics")
        print("=" * 60)
        print(f"Objects processed: {self.stats['objects_processed']}")
        print(f"Records processed: {self.stats['records_processed']}")
        print(f"Batches processed: {self.stats['batches_processed']}")
        print(f"Errors encountered: {self.stats['errors']}")
        print("=" * 60)


def example_multi_object_sync():
    """Example 1: Synchronize multiple objects."""
    print("\n=== Multi-Object Synchronization ===")

    with MPohodaSync(debug=False) as sync:
        # Get object counts
        counts = sync.get_object_count()

        # Sync specific objects
        objects_to_sync = ["Activities", "BusinessPartners", "Banks"]

        for obj_name in objects_to_sync:
            try:
                records = sync.sync_object(obj_name)
                print(f"  Retrieved {len(records)} records from {obj_name}")
            except ObjectNotFoundError:
                logger.warning(f"Object {obj_name} not found")

        # Print statistics
        sync.print_stats()


def example_data_transformation():
    """Example 2: Data transformation pipeline."""
    print("\n=== Data Transformation ===")

    with MPohodaSync() as sync:
        # Read original data
        logger.info("Reading original records...")
        records = sync.sync_object("Activities")

        # Transform data
        logger.info("Transforming records...")
        transformed = sync.transform_records(records)

        # Export transformed data
        logger.info("Exporting transformed data...")
        sync.export_to_json(transformed, "/tmp/activities_transformed.json")

        print(f"  Original: {len(records)} records")
        print(f"  Transformed: {len(transformed)} records")


def example_retry_pattern():
    """Example 3: Resilience with retry pattern."""
    print("\n=== Retry Pattern Example ===")

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            logger.info(f"Attempt {retry_count + 1} of {max_retries}")

            driver = MPohodaDriver.from_env()
            try:
                records = driver.read("Activities", page_size=50)
                logger.info(f"✓ Successfully retrieved {len(records)} records")
                break

            finally:
                driver.close()

        except RateLimitError as e:
            retry_count += 1
            wait_time = e.details.get("retry_after", 10)
            logger.warning(f"Rate limited. Retry after {wait_time}s")

            if retry_count < max_retries:
                import time
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(min(wait_time, 2))  # Cap at 2s for demo
            else:
                logger.error("Max retries exceeded")
                break

        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e.message}")
            break

        except Exception as e:
            retry_count += 1
            logger.warning(f"Error: {e}. Retrying...")


def example_field_discovery():
    """Example 4: Discovering object schemas."""
    print("\n=== Field Discovery ===")

    driver = MPohodaDriver.from_env()

    try:
        # Discover all objects
        objects = driver.list_objects()
        print(f"Available objects ({len(objects)}):")

        # Get fields for each object
        for obj_name in objects[:3]:  # First 3 for demo
            try:
                fields = driver.get_fields(obj_name)
                print(f"\n{obj_name}:")
                print(f"  Fields: {len(fields)}")

                for field_name, field_info in list(fields.items())[:3]:
                    field_type = field_info.get("type", "unknown")
                    required = field_info.get("required", False)
                    print(f"    - {field_name} ({field_type}) {'[REQ]' if required else ''}")

            except ObjectNotFoundError as e:
                logger.warning(f"Cannot get fields for {obj_name}")

    finally:
        driver.close()


def example_capabilities_based_logic():
    """Example 5: Conditional logic based on capabilities."""
    print("\n=== Capabilities-Based Logic ===")

    driver = MPohodaDriver.from_env()

    try:
        capabilities = driver.get_capabilities()

        print("\nCapabilities check:")
        print(f"  Read operations: {capabilities.read}")
        print(f"  Write operations: {capabilities.write}")
        print(f"  Update operations: {capabilities.update}")
        print(f"  Delete operations: {capabilities.delete}")
        print(f"  Max page size: {capabilities.max_page_size}")

        # Conditional logic based on capabilities
        if capabilities.read:
            logger.info("Read operations supported - proceeding with read")
            records = driver.read("Activities", page_size=50)
            logger.info(f"  ✓ Read {len(records)} records")

        if capabilities.write:
            logger.info("Write operations supported")
        else:
            logger.info("Write operations not supported - skipping create")

        if capabilities.update:
            logger.info("Update operations supported")
        else:
            logger.info("Update operations not supported")

        if capabilities.delete:
            logger.info("Delete operations supported")
        else:
            logger.info("Delete operations not supported")

    finally:
        driver.close()


def main():
    """Run all advanced examples."""
    print("=" * 70)
    print("mPOHODA Driver Advanced Usage Examples")
    print("=" * 70)

    # Example 1: Multi-object sync
    example_multi_object_sync()

    # Example 2: Data transformation
    example_data_transformation()

    # Example 3: Retry pattern
    example_retry_pattern()

    # Example 4: Field discovery
    example_field_discovery()

    # Example 5: Capabilities-based logic
    example_capabilities_based_logic()

    print("\n" + "=" * 70)
    print("✅ Advanced examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
