# Apify Driver

Production-ready Python API driver for the Apify platform with automatic retry, pagination, and comprehensive error handling.

## Overview

The **Apify Driver** provides a clean, high-level Python interface to the Apify REST API. It abstracts away common patterns like authentication, pagination, error handling, and rate limit retries so you can focus on your business logic.

### Key Features

- ✅ **Full CRUD Operations** - Create, read, update, delete resources
- ✅ **Automatic Retry** - Exponential backoff on rate limits (HTTP 429)
- ✅ **Offset-Based Pagination** - Memory-efficient batch processing
- ✅ **Structured Error Handling** - 9 exception types with actionable messages
- ✅ **Debug Logging** - Comprehensive debug mode for troubleshooting
- ✅ **Type Hints** - 100% type hint coverage for IDE support
- ✅ **Zero Dependencies** - Only requires `requests` library

### What It Does

```
User Code
    ↓
ApifyDriver (Handles auth, pagination, errors, retries)
    ↓
requests.Session (HTTP)
    ↓
Apify API (https://api.apify.com/v2)
    ↓
Results (parsed, validated, structured)
```

---

## Installation

### Via pip (recommended)

```bash
pip install apify-driver
```

### From source

```bash
git clone <repository>
cd generated_drivers/apify
pip install -e .
```

### Requirements

- Python 3.7+
- `requests` library (automatically installed)

---

## Quick Start

### 1. Get Your API Token

1. Visit https://console.apify.com/settings/integrations
2. Copy your API token
3. Set environment variable:

```bash
export APIFY_API_TOKEN="your_token_here"
```

### 2. Initialize the Driver

```python
from apify_driver import ApifyDriver

# Load credentials from environment
client = ApifyDriver.from_env()
```

### 3. Use the Driver

```python
# List all actors
actors = client.read("/actors", limit=50)
print(f"Found {len(actors)} actors")

# Get actor details
for actor in actors:
    print(f"  - {actor['name']} (ID: {actor['id']})")
```

### 4. Cleanup

```python
client.close()
```

### Complete Example

```python
from apify_driver import ApifyDriver

def main():
    # Initialize
    client = ApifyDriver.from_env()

    try:
        # Get actors
        actors = client.read("/actors", limit=10)
        print(f"Found {len(actors)} actors:")

        for actor in actors:
            print(f"  - {actor['name']}")

    finally:
        client.close()

if __name__ == "__main__":
    main()
```

---

## Authentication

### Environment Variables

Set these environment variables for automatic credential loading:

```bash
# Required
export APIFY_API_TOKEN="your_api_token_here"

# Optional (defaults to https://api.apify.com/v2)
export APIFY_API_URL="https://api.apify.com/v2"
```

### Programmatic Initialization

```python
from apify_driver import ApifyDriver

# Option 1: From environment (recommended)
client = ApifyDriver.from_env()

# Option 2: Explicit credentials
client = ApifyDriver(
    api_url="https://api.apify.com/v2",
    api_key="your_api_token_here"
)

# Option 3: With options
client = ApifyDriver(
    api_url="https://api.apify.com/v2",
    api_key="your_api_token_here",
    timeout=30,          # Request timeout in seconds
    max_retries=3,       # Retry attempts on rate limits
    debug=True           # Enable debug logging
)
```

### Authentication Header

The driver uses **Bearer token** authentication:

```
Authorization: Bearer <your_api_token>
```

**Do NOT include the token in URLs or query parameters** - always use the header method.

### Getting Your Token

1. Log in to https://console.apify.com
2. Go to Settings → Integrations
3. Copy your API token
4. Keep it secret - never commit it to version control

---

## Capabilities

The driver provides the following capabilities:

| Capability | Supported | Notes |
|----------|-----------|-------|
| Read | ✅ Yes | Query and list resources |
| Write | ✅ Yes | Create new resources |
| Update | ✅ Yes | Modify existing resources |
| Delete | ✅ Yes | Delete resources |
| Batch Operations | ✅ Yes | `read_batched()` for memory efficiency |
| Streaming | ✅ Yes | Iterator-based for large datasets |
| Pagination | ✅ Yes | Offset-based (limit, offset) |
| Transactions | ❌ No | REST API doesn't support transactions |

### Supported Resources

The driver works with all Apify resource types:

- **Actors** - Automation scripts and microservices
- **Runs** - Actor execution instances
- **Datasets** - Structured data storage
- **Key-Value Stores** - Key-based data storage
- **Request Queues** - URL queuing for crawling
- **Tasks** - Named Actor configurations
- **Webhooks** - Event notifications
- **Schedules** - Scheduled executions
- **Builds** - Actor build artifacts

```python
# Supported resource types
resources = client.list_objects()
# Returns: ['actors', 'runs', 'datasets', ...]
```

---

## Common Patterns

### Pattern 1: List Resources with Pagination

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    # Get first 50 actors
    actors = client.read("/actors", limit=50, offset=0)
    print(f"Found {len(actors)} actors")

    # Get next 50
    more_actors = client.read("/actors", limit=50, offset=50)
    print(f"Found {len(more_actors)} more actors")

finally:
    client.close()
```

### Pattern 2: Process Large Datasets (Memory-Efficient)

For large datasets, use `read_batched()` to avoid loading everything into memory:

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    dataset_id = "abc123"
    total_processed = 0

    # Process in batches
    for batch in client.read_batched(f"/datasets/{dataset_id}/items", batch_size=100):
        print(f"Processing {len(batch)} records...")
        # Process batch here
        total_processed += len(batch)

    print(f"Total processed: {total_processed} records")

finally:
    client.close()
```

### Pattern 3: Error Handling

```python
from apify_driver import ApifyDriver
from apify_driver import (
    AuthenticationError,
    RateLimitError,
    ObjectNotFoundError,
    ValidationError,
)

client = ApifyDriver.from_env()

try:
    # Try to read a resource
    data = client.read("/invalid-endpoint")

except ObjectNotFoundError as e:
    print(f"Resource not found: {e.message}")
    print(f"Available resources: {client.list_objects()}")

except RateLimitError as e:
    print(f"Rate limited!")
    print(f"Retry after {e.details['retry_after']} seconds")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print("Check your APIFY_API_TOKEN environment variable")

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.details}")

finally:
    client.close()
```

### Pattern 4: Creating Resources

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    # Create a task
    new_task = client.create("tasks", {
        "actId": "actor-id-here",
        "name": "my-task",
        "options": {
            "build": "latest",
            "timeout": 3600
        }
    })

    print(f"Created task: {new_task['id']}")

finally:
    client.close()
```

### Pattern 5: Updating Resources

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    # Update a task
    updated_task = client.update("tasks", "task-id", {
        "name": "updated-name",
        "timeout": 7200
    })

    print(f"Updated task: {updated_task['name']}")

finally:
    client.close()
```

### Pattern 6: Debug Mode

Enable debug logging to see all API calls:

```python
from apify_driver import ApifyDriver

# Initialize with debug=True
client = ApifyDriver.from_env(debug=True)

# All API calls will be logged
actors = client.read("/actors", limit=5)
# Output: [DEBUG] GET https://api.apify.com/v2/actors params={'limit': 5}

client.close()
```

---

## API Reference

### Core Methods

#### `list_objects() -> List[str]`

List all available resource types.

```python
resources = client.list_objects()
# Returns: ['actors', 'runs', 'datasets', 'key-value-stores', ...]
```

#### `get_fields(object_name: str) -> Dict[str, Any]`

Get schema for a resource type.

```python
fields = client.get_fields("actors")
# Returns: {
#   'id': {'type': 'string', 'description': 'Actor ID'},
#   'name': {'type': 'string', 'description': 'Actor name'},
#   ...
# }
```

#### `read(query: str, limit: Optional[int], offset: Optional[int]) -> List[Dict]`

Read resources with optional pagination.

```python
# Basic read
results = client.read("/actors")

# With pagination
results = client.read("/actors", limit=50, offset=0)

# Get specific resource
result = client.read("/runs/run-id")
```

**Parameters:**
- `query` (str) - API endpoint path
- `limit` (int, optional) - Max records to return (max: 100)
- `offset` (int, optional) - Number of records to skip

**Returns:**
- `List[Dict]` - List of resource records

**Raises:**
- `ObjectNotFoundError` - Resource doesn't exist (HTTP 404)
- `QuerySyntaxError` - Invalid query parameters (HTTP 400)
- `RateLimitError` - Rate limit exceeded (HTTP 429, after retries)
- `ConnectionError` - Cannot reach API

#### `read_batched(query: str, batch_size: int) -> Iterator[List[Dict]]`

Read resources in batches (memory-efficient for large datasets).

```python
for batch in client.read_batched("/datasets/xyz/items", batch_size=100):
    print(f"Batch of {len(batch)} records")
    process(batch)
```

**Parameters:**
- `query` (str) - API endpoint path
- `batch_size` (int) - Records per batch (max: 100, default: 100)

**Yields:**
- Batches of records as lists

#### `create(object_name: str, data: Dict[str, Any]) -> Dict[str, Any]`

Create a new resource.

```python
new_task = client.create("tasks", {
    "actId": "actor-123",
    "name": "my-task",
})
```

**Parameters:**
- `object_name` (str) - Resource type (e.g., "tasks", "webhooks")
- `data` (dict) - Resource data

**Returns:**
- `Dict` - Created resource with ID

**Raises:**
- `NotImplementedError` - Resource type doesn't support creation
- `ValidationError` - Invalid data

#### `update(object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]`

Update an existing resource.

```python
updated_task = client.update("tasks", "task-123", {
    "name": "updated-name",
})
```

**Parameters:**
- `object_name` (str) - Resource type
- `record_id` (str) - Resource ID
- `data` (dict) - Fields to update

**Returns:**
- `Dict` - Updated resource

#### `delete(object_name: str, record_id: str) -> bool`

Delete a resource.

```python
success = client.delete("tasks", "task-123")
```

**Parameters:**
- `object_name` (str) - Resource type
- `record_id` (str) - Resource ID

**Returns:**
- `bool` - True if successful

**Note:** Agents should RARELY generate delete operations - always require explicit user approval!

#### `get_capabilities() -> DriverCapabilities`

Get driver capabilities.

```python
capabilities = client.get_capabilities()
print(f"Write support: {capabilities.write}")
print(f"Batch support: {capabilities.batch_operations}")
```

#### `close()`

Close connections and cleanup resources.

```python
try:
    data = client.read("/actors")
finally:
    client.close()  # Always cleanup
```

---

## Rate Limits

Apify API has these rate limits:

| Limit Type | Value |
|-----------|-------|
| Global (authenticated) | 250,000 requests/minute |
| Per-resource (default) | 60 requests/second |
| Key-value store CRUD | 200 requests/second |
| Dataset append | 400 requests/second |

### Handling Rate Limits

The driver automatically handles rate limits:

1. **Automatic Retry** - When HTTP 429 is received, the driver automatically retries with exponential backoff
2. **Configurable Retries** - Set `max_retries` to control retry behavior
3. **Backoff Strategy** - Exponential backoff with factor of 2 (1s, 2s, 4s, 8s, etc.)

```python
# Initialize with custom retry settings
client = ApifyDriver.from_env(max_retries=5)  # Retry up to 5 times

# Or use defaults
client = ApifyDriver.from_env()  # 3 retries by default
```

### Rate Limit Errors

If all retries are exhausted, a `RateLimitError` is raised:

```python
from apify_driver import RateLimitError

try:
    data = client.read("/large-dataset")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.details['retry_after']} seconds")
    # Wait before retrying
    import time
    time.sleep(e.details['retry_after'])
    data = client.read("/large-dataset")
```

### Rate Limit Best Practices

1. **Use Batch Processing** - Use `read_batched()` to spread requests over time
2. **Reduce Batch Size** - Smaller batches = fewer requests
3. **Add Delays** - Add client-side delays between requests
4. **Monitor Usage** - Use `get_rate_limit_status()` to check remaining quota

```python
# Batch processing spreads requests
for batch in client.read_batched("/datasets/xyz/items", batch_size=50):
    # This spreads the load across multiple requests
    process(batch)
    time.sleep(0.1)  # Small delay between batches
```

---

## Troubleshooting

### Authentication Errors

**Error:** `AuthenticationError: Invalid Apify API token`

**Solutions:**
1. Check `APIFY_API_TOKEN` is set: `echo $APIFY_API_TOKEN`
2. Get new token: https://console.apify.com/settings/integrations
3. Verify token has necessary permissions
4. Check token hasn't expired

```bash
export APIFY_API_TOKEN="your_new_token"
```

### Connection Errors

**Error:** `ConnectionError: Cannot reach Apify API`

**Solutions:**
1. Check internet connection: `ping api.apify.com`
2. Verify Apify API is up: https://status.apify.com
3. Check proxy/firewall settings
4. Increase timeout: `ApifyDriver.from_env(timeout=60)`

### Rate Limit Errors

**Error:** `RateLimitError: Rate limit exceeded. Retry after 60 seconds.`

**Solutions:**
1. Reduce batch size: `read_batched(batch_size=25)`
2. Add delays: `time.sleep(0.1)` between batches
3. Reduce request frequency
4. Wait for rate limit window to reset

### Resource Not Found Errors

**Error:** `ObjectNotFoundError: Resource not found: /invalid-endpoint`

**Solutions:**
1. Check resource ID is correct
2. List available resources: `client.list_objects()`
3. Get schema: `client.get_fields("actors")`
4. Check endpoint path is correct

```python
# List available resources
resources = client.list_objects()
print(resources)

# Get schema for resource type
fields = client.get_fields("actors")
print(fields.keys())
```

### Validation Errors

**Error:** `ValidationError: limit cannot exceed 100`

**Solutions:**
1. Check parameter limits - max page size is 100
2. Check required fields are present
3. Check field types match schema

```python
# Correct way - respect limits
results = client.read("/actors", limit=50)  # Max is 100

# Wrong way
results = client.read("/actors", limit=500)  # ERROR - too large
```

### Debug Mode

Enable debug logging to see all API calls:

```python
client = ApifyDriver.from_env(debug=True)

# All API calls will be logged with [DEBUG] prefix
actors = client.read("/actors", limit=5)
# Output:
# [DEBUG] GET https://api.apify.com/v2/actors params={'limit': 5}
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Token not provided" | Set `APIFY_API_TOKEN` environment variable |
| "Cannot reach API" | Check internet connection, verify API URL |
| "Rate limited" | Use `read_batched()`, reduce batch size, add delays |
| "Resource not found" | Verify resource ID, use `list_objects()` |
| "Invalid data" | Check schema with `get_fields()`, fix data types |
| "Timeout after 30s" | Increase timeout: `timeout=60` |
| "Memory issues" | Use `read_batched()` instead of `read()` |

---

## Exception Reference

All exceptions inherit from `DriverError` and include `message` and `details` attributes:

```python
from apify_driver import DriverError

try:
    # API call
    pass
except DriverError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
```

### Exception Types

| Exception | When Raised | HTTP Code |
|-----------|-------------|-----------|
| `AuthenticationError` | Invalid API token | 401 |
| `ConnectionError` | Cannot reach API, network error | N/A |
| `ObjectNotFoundError` | Resource doesn't exist | 404 |
| `FieldNotFoundError` | Field not found on resource | N/A |
| `QuerySyntaxError` | Invalid query parameters | 400 |
| `RateLimitError` | Rate limit exceeded (after retries) | 429 |
| `ValidationError` | Data validation failed | 400 |
| `TimeoutError` | Request timed out | N/A |
| `NotImplementedError` | Operation not supported | N/A |

---

## Agent Integration Guide

If you're generating code with Claude or another agent, the driver provides these APIs:

### Discovery
Agents learn what's available:
```python
resources = client.list_objects()  # ['actors', 'runs', 'datasets', ...]
fields = client.get_fields("actors")  # Get schema
capabilities = client.get_capabilities()  # What driver supports
```

### Common Patterns
Agents generate code following these patterns:

```python
# Pattern 1: Simple read
results = client.read("/actors", limit=50)

# Pattern 2: Pagination
for batch in client.read_batched("/datasets/xyz/items", batch_size=100):
    process(batch)

# Pattern 3: Error handling
try:
    data = client.read("/endpoint")
except ObjectNotFoundError as e:
    print(f"Not found: {e.message}")

# Pattern 4: CRUD operations
created = client.create("tasks", {"actId": "xyz", "name": "task"})
updated = client.update("tasks", "id", {"name": "new-name"})
deleted = client.delete("tasks", "id")
```

### README-Driven Learning
This README teaches agents how to use the driver correctly.

---

## Examples

### Example 1: List All Actors

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    actors = client.read("/actors", limit=100)
    print(f"Found {len(actors)} actors:")
    for actor in actors:
        print(f"  - {actor['name']} (ID: {actor['id']})")
finally:
    client.close()
```

### Example 2: Process Large Dataset

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()

try:
    dataset_id = "my-dataset-123"
    total = 0

    for batch in client.read_batched(f"/datasets/{dataset_id}/items", batch_size=100):
        print(f"Processing {len(batch)} records...")
        # Process batch
        total += len(batch)

    print(f"Total: {total} records processed")
finally:
    client.close()
```

### Example 3: Create and Update Task

```python
from apify_driver import ApifyDriver, ValidationError

client = ApifyDriver.from_env()

try:
    # Create task
    task = client.create("tasks", {
        "actId": "crawler-actor",
        "name": "web-crawler",
        "options": {
            "build": "latest",
            "timeout": 3600
        }
    })
    print(f"Created task: {task['id']}")

    # Update task
    updated = client.update("tasks", task['id'], {
        "name": "updated-crawler",
        "timeout": 7200
    })
    print(f"Updated: {updated['name']}")

except ValidationError as e:
    print(f"Validation error: {e.message}")
finally:
    client.close()
```

---

## Contributing

Found a bug or have a feature request? Please open an issue on GitHub.

### Running Tests

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires APIFY_API_TOKEN)
pytest tests/integration/
```

---

## License

MIT License - see LICENSE file for details

---

## Support

- **Documentation:** https://docs.apify.com
- **API Reference:** https://docs.apify.com/api/v2
- **Issues:** GitHub Issues
- **Community:** Apify Community Forum

---

## Summary

The **Apify Driver** provides a production-ready Python interface to the Apify API. It handles:

- ✅ Authentication and credential management
- ✅ Automatic retry with exponential backoff
- ✅ Offset-based pagination
- ✅ Structured error handling
- ✅ Debug logging
- ✅ Connection validation

**Get started:** `client = ApifyDriver.from_env()`

**Process large datasets:** `for batch in client.read_batched(...)`

**Handle errors:** Catch specific exception types and respond appropriately

See the examples above and troubleshooting section for common patterns and solutions.
