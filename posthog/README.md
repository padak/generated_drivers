# PostHog Python Driver

A production-ready Python driver for the PostHog API with automatic pagination, rate limiting, and comprehensive error handling.

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Specification:** Driver Design v2.0

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Authentication](#authentication)
5. [Capabilities](#capabilities)
6. [Common Patterns](#common-patterns)
7. [API Reference](#api-reference)
8. [Rate Limits](#rate-limits)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Overview

The PostHog Python Driver provides a simple, pythonic interface to the PostHog API. It handles:

- **CRUD Operations** - Create, read, update, delete resources
- **Pagination** - Automatic cursor-based pagination with limit/offset support
- **Rate Limiting** - Automatic retry with exponential backoff
- **Error Handling** - Structured exceptions with actionable suggestions
- **Multi-Region Support** - US Cloud, EU Cloud, or self-hosted instances
- **Resource Discovery** - Introspect available objects and fields

### Key Features

- ✅ Full CRUD support for PostHog resources
- ✅ Automatic pagination with memory-efficient batching
- ✅ Type hints throughout for IDE support
- ✅ Comprehensive docstrings and examples
- ✅ Debug mode for troubleshooting
- ✅ Connection validation at initialization (fail fast!)
- ✅ Resource schema discovery
- ✅ Soft delete support

### Supported Resources

The driver supports all major PostHog resources:

- `batch_exports` - Automated data exports
- `dashboards` - Analytics dashboards
- `datasets` - Reusable datasets
- `dataset_items` - Dataset items
- `desktop_recordings` - Session recordings
- `error_tracking` - Error tracking and grouping
- `endpoints` - Materialized queries
- `persons` - User profiles
- `events` - Event data
- `feature_flags` - Feature flags

---

## Installation

### From PyPI (when published)

```bash
pip install posthog-driver
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/posthog-driver.git
cd posthog-driver

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### Requirements

- Python 3.8+
- `requests` (HTTP library)
- `urllib3` (included with requests)

---

## Quick Start

### Initialize the Driver

```python
from posthog_driver import PostHogDriver

# Load credentials from environment variables
driver = PostHogDriver.from_env()

# Or specify credentials explicitly
driver = PostHogDriver(
    api_url="https://app.posthog.com/api",
    api_key="your_personal_api_key"
)
```

### Discover Resources

```python
# List all available resource types
objects = driver.list_objects()
print(f"Available resources: {objects}")
# Output: ['batch_exports', 'dashboards', 'datasets', ...]

# Get field schema for a resource
fields = driver.get_fields("dashboards")
for field_name, field_info in fields.items():
    print(f"{field_name}: {field_info['type']}")
```

### Read Data

```python
# Fetch dashboards
dashboards = driver.read("/dashboards", limit=50)

for dashboard in dashboards:
    print(f"Dashboard: {dashboard['name']}")
    print(f"  Created: {dashboard['created_at']}")
```

### Create Resources

```python
# Create a new dashboard
dashboard = driver.create("dashboards", {
    "name": "My Dashboard",
    "description": "A test dashboard"
})

print(f"Created dashboard with ID: {dashboard['id']}")
```

### Update Resources

```python
# Update an existing dashboard
updated = driver.update("dashboards", dashboard_id, {
    "name": "Updated Dashboard Name"
})

print(f"Updated: {updated['name']}")
```

### Delete Resources

```python
# Delete a dashboard (soft delete)
success = driver.delete("dashboards", dashboard_id)

if success:
    print("Dashboard deleted")
```

### Cleanup

```python
# Always close the driver when done
driver.close()
```

### Complete Example with Error Handling

```python
from posthog_driver import PostHogDriver, AuthenticationError, RateLimitError

try:
    # Initialize driver
    driver = PostHogDriver.from_env()

    # Get dashboards
    dashboards = driver.read("/dashboards", limit=10)
    print(f"Found {len(dashboards)} dashboards")

    # Create new dashboard
    new_dashboard = driver.create("dashboards", {
        "name": "New Dashboard"
    })
    print(f"Created dashboard: {new_dashboard['id']}")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"Suggestion: {e.details.get('suggestion')}")

except RateLimitError as e:
    retry_after = e.details['retry_after']
    print(f"Rate limited. Retry after {retry_after} seconds")

finally:
    driver.close()
```

---

## Authentication

### Environment Variables (Recommended)

Set environment variables before running your script:

```bash
# Required: Personal API Key
export POSTHOG_API_KEY=your_personal_api_key

# Optional: API URL (defaults to US cloud)
export POSTHOG_API_URL=https://app.posthog.com/api

# Optional: Project ID
export POSTHOG_PROJECT_ID=your_project_id
```

Then initialize the driver:

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()
```

### Explicit Credentials

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver(
    api_url="https://app.posthog.com/api",
    api_key="your_personal_api_key",
    project_id="your_project_id"  # Optional
)
```

### Getting Your Credentials

1. **Personal API Key**
   - Visit your PostHog instance
   - Go to: Account Settings → API
   - Create a new personal API token
   - Copy the token and set `POSTHOG_API_KEY`

2. **Project ID**
   - Visit your PostHog instance
   - Go to: Project Settings
   - Copy the Project ID
   - Set `POSTHOG_PROJECT_ID` (optional, can be inferred)

3. **API URL**
   - **US Cloud:** `https://app.posthog.com/api` (default)
   - **EU Cloud:** `https://eu.posthog.com/api`
   - **Self-Hosted:** `https://your-instance.com/api`

### API Key Scopes

Personal API keys support scope-based permissions:

- `dashboard:read` - Read dashboards
- `dashboard:write` - Create/modify dashboards
- `batch_export:read` - Read batch exports
- `batch_export:write` - Create/modify batch exports
- `INTERNAL` - Privileged operations

Create tokens with minimal required scopes for security.

---

## Capabilities

Check driver capabilities to determine what operations are supported:

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

# Get capabilities
capabilities = driver.get_capabilities()

print(f"Can read: {capabilities.read}")
print(f"Can write: {capabilities.write}")
print(f"Can update: {capabilities.update}")
print(f"Can delete: {capabilities.delete}")
print(f"Supports batch operations: {capabilities.batch_operations}")
print(f"Supports streaming: {capabilities.streaming}")
print(f"Pagination style: {capabilities.pagination}")
print(f"Max page size: {capabilities.max_page_size}")
```

### Output

```
Can read: True
Can write: True
Can update: True
Can delete: True
Supports batch operations: True
Supports streaming: True
Pagination style: PaginationStyle.CURSOR
Max page size: 100
```

---

## Common Patterns

### 1. Reading Data with Pagination

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

# Fetch first page
dashboards = driver.read("/dashboards", limit=50, offset=0)
print(f"Page 1: {len(dashboards)} dashboards")

# Fetch second page
dashboards_page_2 = driver.read("/dashboards", limit=50, offset=50)
print(f"Page 2: {len(dashboards_page_2)} dashboards")

driver.close()
```

### 2. Processing Large Datasets

Use `read_batched()` for memory-efficient processing:

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

total_processed = 0

# Process in batches of 100
for batch in driver.read_batched("/events", batch_size=100):
    print(f"Processing batch of {len(batch)} events")

    # Your processing logic here
    for event in batch:
        print(f"  Event: {event['event']}")

    total_processed += len(batch)

print(f"Total processed: {total_processed} events")
driver.close()
```

### 3. Error Handling with Retries

```python
from posthog_driver import PostHogDriver, RateLimitError
import time

driver = PostHogDriver.from_env()

max_attempts = 3
attempt = 0

while attempt < max_attempts:
    try:
        results = driver.read("/dashboards")
        print(f"Success! Found {len(results)} dashboards")
        break

    except RateLimitError as e:
        attempt += 1
        if attempt >= max_attempts:
            print(f"Failed after {max_attempts} attempts")
            raise

        retry_after = e.details['retry_after']
        print(f"Rate limited. Waiting {retry_after} seconds...")
        time.sleep(retry_after)

finally:
    driver.close()
```

### 4. Creating Multiple Resources

```python
from posthog_driver import PostHogDriver
from posthog_driver import ValidationError

driver = PostHogDriver.from_env()

dashboard_names = [
    "Sales Dashboard",
    "Marketing Dashboard",
    "Analytics Dashboard"
]

for name in dashboard_names:
    try:
        dashboard = driver.create("dashboards", {
            "name": name,
            "description": f"Created programmatically"
        })
        print(f"✓ Created: {name} (ID: {dashboard['id']})")

    except ValidationError as e:
        print(f"✗ Failed to create {name}: {e.message}")

driver.close()
```

### 5. Discovering Resource Schema

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

# Get all available resources
objects = driver.list_objects()
print(f"Available resources: {objects}")

# Inspect each resource type
for obj_name in objects[:3]:  # Show first 3
    fields = driver.get_fields(obj_name)

    print(f"\n{obj_name}:")
    for field_name, field_info in fields.items():
        required = "required" if field_info.get('required') else "optional"
        print(f"  - {field_name}: {field_info['type']} ({required})")

driver.close()
```

### 6. Conditional Operations

```python
from posthog_driver import PostHogDriver, ObjectNotFoundError

driver = PostHogDriver.from_env()

dashboard_id = "some-dashboard-id"

try:
    # Try to get the dashboard
    dashboard = driver.read(f"/dashboards/{dashboard_id}")

except ObjectNotFoundError as e:
    print(f"Dashboard not found: {e.message}")
    print(f"Available: {e.details.get('available', [])}")

driver.close()
```

### 7. Debug Mode for Troubleshooting

```python
from posthog_driver import PostHogDriver

# Enable debug mode to see all API calls
driver = PostHogDriver.from_env(debug=True)

# Now all operations will log details
dashboards = driver.read("/dashboards", limit=5)

# Output will include:
# [DEBUG] Session created with retry strategy: ...
# [DEBUG] GET https://app.posthog.com/api/environments/default/dashboards/...
# [DEBUG] Parsed wrapped response with X records

driver.close()
```

---

## API Reference

### PostHogDriver Class

#### Initialization

```python
driver = PostHogDriver(
    api_url: str = "https://app.posthog.com/api",
    api_key: Optional[str] = None,
    project_id: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 3,
    debug: bool = False
)
```

**Parameters:**

- `api_url` - PostHog API base URL (default: US cloud)
- `api_key` - Personal API key (loaded from POSTHOG_API_KEY if not provided)
- `project_id` - PostHog project ID (optional)
- `timeout` - Request timeout in seconds (default: 30)
- `max_retries` - Retry attempts on rate limit (default: 3)
- `debug` - Enable debug logging (default: False)

**Raises:**

- `AuthenticationError` - If API key is invalid or missing
- `ConnectionError` - If cannot reach PostHog API

#### Class Methods

##### `from_env() -> PostHogDriver`

Create driver from environment variables.

```python
driver = PostHogDriver.from_env()
```

**Environment Variables:**

- `POSTHOG_API_KEY` (required)
- `POSTHOG_API_URL` (optional, default: US cloud)
- `POSTHOG_PROJECT_ID` (optional)

**Raises:**

- `AuthenticationError` - If POSTHOG_API_KEY is not set

#### Instance Methods

##### `get_capabilities() -> DriverCapabilities`

Get driver capabilities.

```python
capabilities = driver.get_capabilities()

if capabilities.write:
    # Can create new resources
    pass
```

**Returns:**

- `DriverCapabilities` - Object with feature flags and limits

##### `list_objects() -> List[str]`

List all available resource types.

```python
objects = driver.list_objects()
# ['batch_exports', 'dashboards', 'datasets', ...]
```

**Returns:**

- List of resource type names

##### `get_fields(object_name: str) -> Dict[str, Any]`

Get field schema for a resource type.

```python
fields = driver.get_fields("dashboards")
# {
#   "id": {"type": "string", "required": False, ...},
#   "name": {"type": "string", "required": True, ...},
#   ...
# }
```

**Parameters:**

- `object_name` - Resource type name

**Returns:**

- Dictionary mapping field names to field metadata

**Raises:**

- `ObjectNotFoundError` - If resource type not found

##### `read(query: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict]`

Execute a read query.

```python
results = driver.read("/dashboards", limit=50)
```

**Parameters:**

- `query` - Endpoint path (e.g., "/dashboards")
- `limit` - Maximum records (max: 100, default: 50)
- `offset` - Records to skip (for pagination)

**Returns:**

- List of records

**Raises:**

- `ValidationError` - If limit exceeds maximum
- `RateLimitError` - If rate limit exceeded
- `ConnectionError` - If network error

##### `read_batched(query: str, batch_size: int = 1000) -> Iterator[List[Dict]]`

Read data in batches (memory-efficient).

```python
for batch in driver.read_batched("/events", batch_size=100):
    process_batch(batch)
```

**Parameters:**

- `query` - Endpoint path
- `batch_size` - Records per batch (max: 100)

**Yields:**

- Batches of records

**Raises:**

- `ValidationError` - If batch_size exceeds maximum

##### `create(object_name: str, data: Dict[str, Any]) -> Dict[str, Any]`

Create a new resource.

```python
dashboard = driver.create("dashboards", {
    "name": "My Dashboard",
    "description": "Test"
})
```

**Parameters:**

- `object_name` - Resource type
- `data` - Resource data

**Returns:**

- Created resource with ID

**Raises:**

- `ValidationError` - If data is invalid
- `ObjectNotFoundError` - If resource type not found

##### `update(object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]`

Update an existing resource.

```python
updated = driver.update("dashboards", "123", {
    "name": "Updated Name"
})
```

**Parameters:**

- `object_name` - Resource type
- `record_id` - Resource ID
- `data` - Fields to update

**Returns:**

- Updated resource

**Raises:**

- `ObjectNotFoundError` - If resource not found
- `ValidationError` - If data is invalid

##### `delete(object_name: str, record_id: str) -> bool`

Delete a resource (soft delete).

```python
success = driver.delete("dashboards", "123")
```

**Parameters:**

- `object_name` - Resource type
- `record_id` - Resource ID

**Returns:**

- True if successful

**Raises:**

- `ObjectNotFoundError` - If resource not found

##### `call_endpoint(endpoint: str, method: str = "GET", params: Optional[Dict] = None, data: Optional[Dict] = None, **kwargs) -> Dict`

Call a REST endpoint directly.

```python
result = driver.call_endpoint(
    endpoint="/dashboards",
    method="GET",
    params={"limit": 50}
)
```

**Parameters:**

- `endpoint` - API endpoint path
- `method` - HTTP method (GET, POST, PATCH, DELETE)
- `params` - URL query parameters
- `data` - Request body (for POST/PATCH)

**Returns:**

- Response data

##### `get_rate_limit_status() -> Dict[str, Any]`

Get current rate limit status.

```python
status = driver.get_rate_limit_status()
if status["remaining"] is not None:
    print(f"Requests remaining: {status['remaining']}")
```

**Returns:**

- Dictionary with rate limit information (when available)

##### `close()`

Close the driver and cleanup resources.

```python
driver.close()
```

---

## Rate Limits

PostHog API enforces rate limits on private endpoints (organization-wide):

| Endpoint Category | Limit | Period |
|---|---|---|
| Analytics endpoints | 240 | per minute |
| Analytics endpoints | 1200 | per hour |
| Query endpoint | 2400 | per hour |
| Feature flag local evaluation | 600 | per minute |
| CRUD operations | 480 | per minute |
| CRUD operations | 4800 | per hour |
| Public POST endpoints | Unlimited | - |

### Rate Limit Handling

The driver automatically handles rate limits:

1. **Automatic Retry** - On 429 (Too Many Requests), retries with exponential backoff
2. **Exponential Backoff** - Waits 1s, 2s, 4s, 8s between retries
3. **Max Retries** - Configurable (default: 3 attempts)
4. **Respects Headers** - Uses `Retry-After` header from API

### Configuration

```python
# Increase retry attempts for high-load scenarios
driver = PostHogDriver.from_env(max_retries=5)

# Disable retries (not recommended)
driver = PostHogDriver.from_env(max_retries=0)
```

### Handling Rate Limit Errors

```python
from posthog_driver import RateLimitError
import time

try:
    results = driver.read("/dashboards")

except RateLimitError as e:
    retry_after = e.details['retry_after']
    print(f"Rate limited. Retry after {retry_after}s")
    time.sleep(retry_after)
    results = driver.read("/dashboards")
```

### Best Practices

1. **Batch Operations** - Use `read_batched()` to process large datasets efficiently
2. **Reduce Batch Size** - Smaller batches consume fewer API calls
3. **Add Delays** - Insert delays between requests if needed
4. **Monitor Usage** - Check `get_rate_limit_status()` periodically
5. **Cache Results** - Cache query results to avoid repeated calls

---

## Troubleshooting

### Authentication Errors

#### Error: "Missing PostHog API key"

**Cause:** POSTHOG_API_KEY environment variable not set

**Solution:**

```bash
export POSTHOG_API_KEY=your_personal_api_key
```

Or provide explicitly:

```python
driver = PostHogDriver(api_key="your_personal_api_key")
```

#### Error: "Invalid PostHog API key"

**Cause:** API key is incorrect or has insufficient permissions

**Solution:**

1. Verify the API key is correct
2. Check that the key has required scopes (e.g., `dashboard:read`)
3. Generate a new API key if needed

### Connection Errors

#### Error: "Cannot reach PostHog API"

**Cause:** Network issue or incorrect API URL

**Solution:**

1. Check internet connection
2. Verify API URL is correct:
   - US: `https://app.posthog.com/api`
   - EU: `https://eu.posthog.com/api`
3. Check firewall/proxy settings

```python
# Explicit API URL
driver = PostHogDriver(
    api_url="https://app.posthog.com/api",
    api_key="your_key"
)
```

#### Error: "Request timed out"

**Cause:** API is slow or timeout is too short

**Solution:**

```python
# Increase timeout
driver = PostHogDriver.from_env(timeout=60)
```

### Resource Not Found

#### Error: "Object 'dashboards' not found"

**Cause:** Incorrect resource type name

**Solution:**

1. List available resources:

```python
objects = driver.list_objects()
print(objects)
```

2. Use correct resource name

#### Error: "Resource '123' not found"

**Cause:** Resource ID is invalid or doesn't exist

**Solution:**

```python
# Check if resource exists
try:
    resource = driver.read(f"/dashboards/123")
except ObjectNotFoundError:
    print("Resource not found")
    print("Available resources:", driver.list_objects())
```

### Validation Errors

#### Error: "limit cannot exceed 100"

**Cause:** Page size parameter exceeds maximum

**Solution:**

```python
# Use valid page size
results = driver.read("/dashboards", limit=100)

# Or use default
results = driver.read("/dashboards")  # Uses default 50
```

### Rate Limit Errors

#### Error: "API rate limit exceeded"

**Cause:** Too many requests in short time

**Solution:**

1. Implement exponential backoff (automatic)
2. Reduce batch size:

```python
# Smaller batches, fewer API calls
for batch in driver.read_batched("/events", batch_size=50):
    process_batch(batch)
```

3. Add delays between requests:

```python
import time

for batch in driver.read_batched("/events", batch_size=100):
    process_batch(batch)
    time.sleep(1)  # 1 second between batches
```

### Debug Mode

Enable debug mode to troubleshoot issues:

```python
driver = PostHogDriver.from_env(debug=True)

# All API calls will be logged
dashboards = driver.read("/dashboards")
```

**Debug output includes:**

- Session creation details
- API request details (method, URL, params)
- Response status and parsing
- Retry attempts
- Connection validation steps

---

## Examples

### Example 1: List All Dashboards

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

try:
    dashboards = driver.read("/dashboards", limit=100)

    print(f"Found {len(dashboards)} dashboards:\n")

    for dashboard in dashboards:
        print(f"- {dashboard['name']}")
        if dashboard.get('description'):
            print(f"  Description: {dashboard['description']}")
        print(f"  Created: {dashboard['created_at']}\n")

finally:
    driver.close()
```

### Example 2: Create Dashboard with Tiles

```python
from posthog_driver import PostHogDriver, ValidationError

driver = PostHogDriver.from_env()

try:
    # Create dashboard
    dashboard = driver.create("dashboards", {
        "name": "Sales Metrics",
        "description": "Key sales KPIs"
    })

    print(f"Created dashboard: {dashboard['id']}")

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Missing fields: {e.details.get('missing_fields')}")

finally:
    driver.close()
```

### Example 3: Process Events in Batches

```python
from posthog_driver import PostHogDriver

driver = PostHogDriver.from_env()

total_events = 0
event_types = {}

try:
    # Process events in batches
    for batch in driver.read_batched("/events", batch_size=1000):
        total_events += len(batch)

        # Count event types
        for event in batch:
            event_type = event.get('event', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print(f"Processed {total_events} events...")

    print(f"\nTotal: {total_events} events")
    print(f"Event types: {event_types}")

finally:
    driver.close()
```

### Example 4: Update Dashboard

```python
from posthog_driver import PostHogDriver, ObjectNotFoundError

driver = PostHogDriver.from_env()

dashboard_id = "your-dashboard-id"

try:
    # Update dashboard
    updated = driver.update("dashboards", dashboard_id, {
        "name": "Updated Dashboard Name",
        "description": "New description"
    })

    print(f"Updated: {updated['name']}")

except ObjectNotFoundError as e:
    print(f"Dashboard not found: {e.message}")

finally:
    driver.close()
```

### Example 5: Delete Old Dashboards

```python
from posthog_driver import PostHogDriver
from datetime import datetime, timedelta

driver = PostHogDriver.from_env()

try:
    dashboards = driver.read("/dashboards", limit=100)

    # Find dashboards older than 30 days
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    for dashboard in dashboards:
        created = datetime.fromisoformat(
            dashboard['created_at'].replace('Z', '+00:00')
        )

        if created < cutoff_date:
            driver.delete("dashboards", dashboard['id'])
            print(f"Deleted: {dashboard['name']}")

finally:
    driver.close()
```

---

## Support & Resources

### Documentation

- [PostHog API Docs](https://posthog.com/docs/api)
- [PostHog Schema Reference](https://app.posthog.com/api/schema/)

### Getting Help

1. **Check Troubleshooting Section** - Common issues and solutions
2. **Enable Debug Mode** - See detailed API call logs
3. **Check Exception Details** - Error messages include suggestions
4. **Review Examples** - See common usage patterns

### Error Messages

All exceptions include:

- **message** - Clear description of what went wrong
- **details** - Structured data with context
- **suggestion** - How to fix the issue

Example:

```python
try:
    driver.read("/invalid_endpoint")
except ObjectNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
    print(f"Fix: {e.details.get('suggestion')}")
```

---

## License

MIT

---

## Changelog

### 1.0.0 (2025-11-19)

- Initial release
- Full CRUD support
- Automatic pagination and rate limiting
- Comprehensive error handling
- Multi-region support
- Debug mode

---

**Version:** 1.0.0
**Last Updated:** 2025-11-19
**Status:** ✅ Production Ready
