# Amplitude Analytics Driver

A production-ready Python driver for Amplitude's analytics APIs with automatic retry, comprehensive error handling, and full type hints.

**Version:** 1.0.0 | **Status:** Production Ready | **Python:** 3.8+

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
9. [Error Handling](#error-handling)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The Amplitude Analytics Driver provides a Python interface to Amplitude's core analytics APIs:

- **Batch Event Upload API** - Ingest events in bulk (up to 2000 per batch)
- **Identify API** - Update user properties without sending events
- **Export API** - Export historical event data by time range

### Key Features

- ✅ **Batch Operations** - Upload up to 2000 events per batch (max 20MB)
- ✅ **Automatic Retry** - Exponential backoff on rate limits (429 responses)
- ✅ **Error Handling** - 8 structured exception types with actionable messages
- ✅ **Type Safe** - 100% type hints for IDE autocomplete
- ✅ **Production Ready** - Fail-fast validation, connection pooling, debug logging
- ✅ **Agent Friendly** - Discoverable objects and fields, structured error details

### What Problems Does This Solve?

| Problem | Solution |
|---------|----------|
| Tedious retry logic | Automatic exponential backoff on rate limits |
| Unclear API errors | Structured exceptions with actionable suggestions |
| Type errors in production | 100% type hints catch errors at development time |
| Missing context on errors | Detailed error details dict for programmatic handling |
| Credential leaks | Environment variable support, no hardcoded keys |
| Connection failures | Validation at init, timeout handling, proper cleanup |

---

## Installation

### Via pip (After Publishing to PyPI)

```bash
pip install amplitude-driver
```

### From Source

```bash
git clone https://github.com/your-repo/amplitude-driver
cd amplitude-driver
pip install -e .
```

### Requirements

- Python 3.8+
- requests >= 2.28.0
- urllib3 >= 1.26.0

---

## Quick Start

### 1. Set Your API Key

```bash
export AMPLITUDE_API_KEY="your_amplitude_api_key"
```

### 2. Import and Initialize

```python
from amplitude import AmplitudeDriver

# Load from environment
driver = AmplitudeDriver.from_env()
```

### 3. Upload Events

```python
# Single event
result = driver.create("events", {
    "user_id": "user123",
    "event_type": "page_view",
    "event_properties": {
        "page": "/home",
        "referrer": "google"
    }
})

# Multiple events (recommended for bulk operations)
events = [
    {
        "user_id": "user1",
        "event_type": "signup",
        "time": 1699400000000,
        "event_properties": {"plan": "premium"}
    },
    {
        "user_id": "user2",
        "event_type": "login",
        "time": 1699400001000
    },
]

result = driver.create_batch(events)
print(f"Ingested {result['events_ingested']} events")
```

### 4. Update User Properties

```python
driver.update("users", "user123", {
    "user_properties": {
        "$set": {"plan": "premium", "signup_date": "2025-01-01"},
        "$add": {"credits": 100}
    }
})
```

### 5. Cleanup

```python
driver.close()

# Or use context manager (recommended):
with AmplitudeDriver.from_env() as driver:
    result = driver.create_batch(events)
    # Automatically cleaned up when exiting the block
```

---

## Authentication

### Environment Variables

The driver loads credentials from environment variables:

```bash
# Required
export AMPLITUDE_API_KEY="your_api_key"

# Optional
export AMPLITUDE_BASE_URL="https://api2.amplitude.com"  # Default
export AMPLITUDE_DEBUG="false"  # Enable debug logging
```

### Explicit Credentials

```python
from amplitude import AmplitudeDriver

driver = AmplitudeDriver(
    api_key="your_api_key",
    base_url="https://api2.amplitude.com",
    timeout=30,
    max_retries=3,
    debug=False
)
```

### From Environment

```python
from amplitude import AmplitudeDriver

# Reads AMPLITUDE_API_KEY from environment
driver = AmplitudeDriver.from_env()

# Raises AuthenticationError if AMPLITUDE_API_KEY not set
```

### EU Region

For EU residency server, set the base URL:

```python
driver = AmplitudeDriver(
    api_key="your_api_key",
    base_url="https://api.eu.amplitude.com"
)
```

---

## Capabilities

### What This Driver Can Do

```python
from amplitude import AmplitudeDriver

driver = AmplitudeDriver.from_env()

# Discover capabilities
capabilities = driver.get_capabilities()
print(f"Read: {capabilities.read}")           # True
print(f"Write: {capabilities.write}")         # True
print(f"Update: {capabilities.update}")       # True
print(f"Delete: {capabilities.delete}")       # False
print(f"Batch: {capabilities.batch_operations}")  # True
print(f"Max page size: {capabilities.max_page_size}")  # 2000
```

### Available Objects

```python
# Discover available objects
objects = driver.list_objects()
# Returns: ['events', 'users', 'user_properties', 'annotations']

# Get field schema for an object
fields = driver.get_fields("events")
# Returns: {
#     "user_id": {"type": "string", "required": True, ...},
#     "event_type": {"type": "string", "required": True, ...},
#     "time": {"type": "integer", "required": False, ...},
#     ...
# }
```

### API Features

| Feature | Status | Details |
|---------|--------|---------|
| **Read Events** | ✅ | Export historical data via Export API |
| **Write Events** | ✅ | Batch upload (max 2000 events, 20MB) |
| **Update Users** | ✅ | User property updates via Identify API |
| **Delete Events** | ❌ | Not supported by Amplitude |
| **Batch Operations** | ✅ | Supported (max 2000 events per batch) |
| **Rate Limiting** | ✅ | Automatic retry with exponential backoff |
| **Property Operations** | ✅ | $set, $setOnce, $add, $append, $prepend, $unset |

---

## Common Patterns

### Pattern 1: Batch Event Upload

Upload multiple events efficiently:

```python
from amplitude import AmplitudeDriver

driver = AmplitudeDriver.from_env()

events = [
    {
        "user_id": "user1",
        "event_type": "page_view",
        "time": 1699400000000,
        "event_properties": {"page": "/home"}
    },
    {
        "user_id": "user2",
        "event_type": "click",
        "time": 1699400001000,
        "event_properties": {"button": "signup"}
    },
]

try:
    result = driver.create_batch(events)
    print(f"Success: Ingested {result['events_ingested']} events")
    print(f"Payload size: {result['payload_size_bytes']} bytes")
except ValidationError as e:
    print(f"Validation failed: {e.details}")
finally:
    driver.close()
```

### Pattern 2: User Property Updates

Update user properties without sending events:

```python
driver = AmplitudeDriver.from_env()

# Set user properties
driver.update("users", "user123", {
    "user_properties": {
        "$set": {
            "plan": "premium",
            "signup_date": "2025-01-01",
            "credits": 100
        }
    }
})

# Use property operations
driver.update("users", "user123", {
    "user_properties": {
        "$set": {"last_login": "2025-01-15"},
        "$add": {"login_count": 1},  # Increment counter
        "$append": {"interests": "music"}  # Add to list
    }
})

driver.close()
```

### Pattern 3: Error Handling

Handle errors gracefully:

```python
from amplitude import AmplitudeDriver
from amplitude.exceptions import (
    AuthenticationError,
    RateLimitError,
    ValidationError,
    ConnectionError
)

try:
    driver = AmplitudeDriver.from_env()
    result = driver.create_batch(events)

except AuthenticationError as e:
    print(f"Auth error: {e.message}")
    print(f"Check: {e.details.get('suggestion')}")

except RateLimitError as e:
    print(f"Rate limited!")
    print(f"Retry after: {e.details['retry_after']} seconds")
    # Driver already retried automatically up to max_retries times

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Details: {e.details}")

except ConnectionError as e:
    print(f"Connection error: {e.message}")
    print(f"Suggestion: {e.details.get('suggestion')}")

finally:
    if 'driver' in locals():
        driver.close()
```

### Pattern 4: Retry with Backoff

Configure retry behavior:

```python
from amplitude import AmplitudeDriver

# High-volume scenario: more retries
driver = AmplitudeDriver.from_env(max_retries=5)

# Testing scenario: no retries
driver = AmplitudeDriver.from_env(max_retries=0)

# Custom timeout
driver = AmplitudeDriver.from_env(timeout=60)
```

### Pattern 5: Debug Logging

Enable debug logging for troubleshooting:

```python
from amplitude import AmplitudeDriver

driver = AmplitudeDriver.from_env(debug=True)

# Now all API calls are logged:
# [DEBUG] POST https://api2.amplitude.com/batch
# [DEBUG] Rate limited. Retrying in 2s (attempt 1/3)
# [DEBUG] POST https://api2.amplitude.com/batch (retry)

result = driver.create_batch(events)
```

### Pattern 6: Context Manager

Use context manager for automatic cleanup:

```python
from amplitude import AmplitudeDriver

# Automatically closes connection when exiting block
with AmplitudeDriver.from_env() as driver:
    result = driver.create_batch(events)
    print(f"Ingested {result['events_ingested']} events")
    # driver.close() called automatically
```

---

## API Reference

### AmplitudeDriver

Main driver class for Amplitude Analytics APIs.

#### Initialization

```python
AmplitudeDriver(
    base_url: str = "https://api2.amplitude.com",
    api_key: Optional[str] = None,
    access_token: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 3,
    debug: bool = False
) -> AmplitudeDriver
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | `https://api2.amplitude.com` | API endpoint URL |
| `api_key` | str | None | Amplitude API key (required) |
| `access_token` | str | None | OAuth token (for future APIs) |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Retry attempts on rate limit |
| `debug` | bool | False | Enable debug logging |

**Raises:**

- `AuthenticationError` - Missing or invalid credentials
- `ConnectionError` - Cannot reach API

**Example:**

```python
driver = AmplitudeDriver(
    api_key="your_api_key",
    timeout=60,
    max_retries=5,
    debug=True
)
```

#### Class Methods

##### `from_env(**kwargs) -> AmplitudeDriver`

Create driver from environment variables.

**Environment Variables:**

- `AMPLITUDE_API_KEY` (required) - Your API key
- `AMPLITUDE_BASE_URL` (optional) - Custom endpoint
- `AMPLITUDE_DEBUG` (optional) - Enable debug mode

**Returns:** Configured `AmplitudeDriver` instance

**Raises:** `AuthenticationError` if `AMPLITUDE_API_KEY` not set

**Example:**

```python
driver = AmplitudeDriver.from_env()
```

#### Instance Methods

##### `get_capabilities() -> DriverCapabilities`

Get driver capabilities.

**Returns:** `DriverCapabilities` with feature flags

**Example:**

```python
caps = driver.get_capabilities()
if caps.batch_operations:
    print("Batch operations supported")
```

##### `list_objects() -> List[str]`

Discover available objects.

**Returns:** List of object names

**Example:**

```python
objects = driver.list_objects()
# Returns: ['events', 'users', 'user_properties', 'annotations']
```

##### `get_fields(object_name: str) -> Dict[str, Any]`

Get field schema for an object.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `object_name` | str | Name of object (case-sensitive) |

**Returns:** Dictionary with field definitions

**Raises:** `ObjectNotFoundError` if object doesn't exist

**Example:**

```python
fields = driver.get_fields("events")
# Returns:
# {
#     "user_id": {
#         "type": "string",
#         "required": False,
#         "label": "User ID"
#     },
#     ...
# }
```

##### `create(object_name: str, data: Dict[str, Any]) -> Dict[str, Any]`

Create a new record (single event).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `object_name` | str | "events" (only supported) |
| `data` | dict | Event data |

**Returns:** Response with ingestion status

**Raises:**
- `ObjectNotFoundError` - Wrong object type
- `ValidationError` - Invalid data
- `RateLimitError` - Rate limit exceeded

**Example:**

```python
result = driver.create("events", {
    "user_id": "user123",
    "event_type": "signup",
    "event_properties": {"plan": "premium"}
})
# Returns: {"code": 200, "events_ingested": 1, ...}
```

##### `create_batch(events: List[Dict[str, Any]]) -> Dict[str, Any]`

Upload multiple events in batch (recommended).

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `events` | list | List of event dictionaries (max 2000) |

**Returns:** Response with ingestion statistics

**Raises:**
- `ValidationError` - Batch exceeds limits
- `RateLimitError` - Rate limit exceeded
- `ConnectionError` - API unreachable

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | int | 200 on success |
| `events_ingested` | int | Number of events processed |
| `payload_size_bytes` | int | Request payload size |
| `server_upload_time` | int | Server timestamp (milliseconds) |

**Example:**

```python
events = [
    {"user_id": "u1", "event_type": "signup"},
    {"user_id": "u2", "event_type": "login"},
]
result = driver.create_batch(events)
print(f"Ingested: {result['events_ingested']}")
```

##### `update(object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]`

Update user properties.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `object_name` | str | "users" (only supported) |
| `record_id` | str | User ID to update |
| `data` | dict | Properties to update |

**Returns:** API response

**Raises:**
- `ObjectNotFoundError` - Wrong object type
- `ValidationError` - Invalid data

**Property Operations Supported:**

| Operation | Description |
|-----------|-------------|
| `$set` | Set property value |
| `$setOnce` | Set only if not already set |
| `$add` | Add numeric value (increment) |
| `$append` | Append to list/array |
| `$prepend` | Prepend to list/array |
| `$unset` | Remove property |

**Example:**

```python
driver.update("users", "user123", {
    "user_properties": {
        "$set": {"plan": "premium"},
        "$add": {"credits": 100},
        "$append": {"interests": "music"}
    }
})
```

##### `read(query: str, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]`

Export historical event data.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | str | Query spec: "start=YYYYMMDDTHH&end=YYYYMMDDTHH" |
| `limit` | int | Not used for Export API |
| `offset` | int | Not used for Export API |

**Returns:** List of events

**Raises:**
- `QuerySyntaxError` - Invalid query format
- `ConnectionError` - API unreachable

**Query Format:**

- `start` and `end` required in format: `YYYYMMDDTHH`
- Example: `start=20250101T00&end=20250101T23`
- Max query range: 365 days
- Max response size: 4GB

**Example:**

```python
# Export data for Jan 1, 2025
events = driver.read("start=20250101T00&end=20250101T23")
print(f"Exported {len(events)} events")
```

##### `close()`

Close connection and cleanup resources.

**Example:**

```python
driver.close()

# Or use context manager:
with AmplitudeDriver.from_env() as driver:
    # ... use driver ...
    pass  # Automatically closed
```

##### `get_rate_limit_status() -> Dict[str, Any]`

Get rate limit status.

**Returns:** Dictionary with rate limit information

**Note:** Amplitude doesn't provide rate limit headers in responses

**Example:**

```python
status = driver.get_rate_limit_status()
# Returns: {
#     "remaining": None,
#     "limit": None,
#     "reset_at": None,
#     "retry_after": None,
#     "note": "Amplitude does not expose rate limit headers"
# }
```

---

## Rate Limits

Amplitude enforces several rate limits that the driver handles automatically:

### Batch Event Upload

| Limit | Value | Action |
|-------|-------|--------|
| Events per batch | 2000 | Validated before sending |
| Payload size | 20MB | Raises 413 if exceeded |
| Events per second (per device/user) | 1000 | Automatic retry (429) |
| Daily events (per device/user) | 500,000 | Raises 429 after daily limit |

### Identify API

| Limit | Value |
|-------|-------|
| User property updates per hour (per user) | 1800 |
| Min ID length | 5 characters |

### Export API

| Limit | Value |
|-------|-------|
| Max query range | 365 days |
| Max response size | 4GB |
| Data availability delay | 2 hours |

### Automatic Retry

The driver automatically retries on rate limits (429 responses):

```python
# Configuration
driver = AmplitudeDriver.from_env(
    max_retries=3,  # Default: 3 retries
    timeout=30      # Default: 30 seconds
)

# Retry strategy:
# Attempt 1: Immediate
# Attempt 2: Wait 1 second (2^0)
# Attempt 3: Wait 2 seconds (2^1)
# Attempt 4: Wait 4 seconds (2^2)
# After max_retries exhausted: Raises RateLimitError
```

### Rate Limit Handling

```python
from amplitude.exceptions import RateLimitError

try:
    driver.create_batch(events)
except RateLimitError as e:
    # Driver already retried automatically
    retry_after = e.details['retry_after']
    print(f"Still rate limited. Wait {retry_after}s before retrying.")

    # Reduce batch size for next attempt
    smaller_batch = events[:1000]
    result = driver.create_batch(smaller_batch)
```

---

## Error Handling

### Exception Hierarchy

All exceptions inherit from `DriverError`:

```python
from amplitude.exceptions import (
    DriverError,                # Base class
    AuthenticationError,         # Invalid credentials
    ConnectionError,             # Cannot reach API
    ObjectNotFoundError,         # Object doesn't exist
    FieldNotFoundError,          # Field doesn't exist
    QuerySyntaxError,            # Invalid query
    RateLimitError,              # Rate limit exceeded
    ValidationError,             # Data validation failed
    TimeoutError,                # Request timeout
)
```

### Error Structure

Every exception includes:

```python
try:
    driver.create_batch(huge_batch)
except ValidationError as e:
    print(f"Message: {e.message}")           # Clear message
    print(f"Details: {e.details}")           # Structured data
    print(f"Suggestion: {e.details.get('suggestion')}")  # How to fix
```

### Common Errors and Solutions

#### AuthenticationError

```python
try:
    driver = AmplitudeDriver.from_env()
except AuthenticationError as e:
    print("Solution: Set AMPLITUDE_API_KEY environment variable")
    print("Command: export AMPLITUDE_API_KEY='your_key'")
```

#### RateLimitError

```python
try:
    driver.create_batch(large_events)
except RateLimitError as e:
    print(f"Retry after {e.details['retry_after']} seconds")
    # Reduce batch size for next attempt
    smaller_batch = large_events[:1000]
    driver.create_batch(smaller_batch)
```

#### ValidationError

```python
try:
    driver.create_batch(events)
except ValidationError as e:
    print(f"Invalid data: {e.message}")
    print(f"Check fields: {e.details.get('missing_fields')}")
    # Fix and retry
```

#### ConnectionError

```python
try:
    driver = AmplitudeDriver(api_key="key", base_url="wrong_url")
except ConnectionError as e:
    print(f"Can't reach API: {e.details['api_url']}")
    print("Solution: Check base_url is correct")
```

---

## Troubleshooting

### Issue: "AuthenticationError: Missing Amplitude API key"

**Cause:** Environment variable not set

**Solution:**

```bash
# Check if set
echo $AMPLITUDE_API_KEY

# Set it
export AMPLITUDE_API_KEY="your_api_key_from_amplitude"

# Verify
echo $AMPLITUDE_API_KEY
```

### Issue: "ConnectionError: Cannot reach API"

**Cause:** Network issue, wrong URL, or Amplitude API down

**Solutions:**

```python
# Check URL is correct
driver = AmplitudeDriver(
    api_key="your_key",
    base_url="https://api2.amplitude.com"  # Correct URL
)

# Check internet connection
import requests
requests.get("https://api2.amplitude.com")

# Use EU endpoint if needed
driver = AmplitudeDriver(
    api_key="your_key",
    base_url="https://api.eu.amplitude.com"
)

# Increase timeout
driver = AmplitudeDriver.from_env(timeout=60)
```

### Issue: "RateLimitError: Rate limit exceeded"

**Cause:** Too many requests too fast, or daily quota exceeded

**Solutions:**

```python
# Reduce batch size
smaller_batch = events[:1000]  # Instead of 2000
result = driver.create_batch(smaller_batch)

# Add delay between requests
import time
for batch in chunks(events, 1000):
    driver.create_batch(batch)
    time.sleep(1)

# Configure retries
driver = AmplitudeDriver.from_env(max_retries=5)
```

### Issue: "ValidationError: Batch size cannot exceed 2000"

**Cause:** Sending too many events in one batch

**Solution:**

```python
# Split into smaller batches
batch_size = 2000
for i in range(0, len(events), batch_size):
    batch = events[i:i+batch_size]
    driver.create_batch(batch)
```

### Issue: "TimeoutError: Request timed out"

**Cause:** Request takes too long

**Solutions:**

```python
# Increase timeout
driver = AmplitudeDriver.from_env(timeout=60)

# Reduce batch size
smaller_batch = events[:1000]
driver.create_batch(smaller_batch)

# Check network latency
import time
start = time.time()
driver.create_batch(small_test_batch)
elapsed = time.time() - start
print(f"Request took {elapsed}s")
```

### Issue: "Events not appearing in Amplitude"

**Causes and Solutions:**

```python
# 1. Check required fields are present
event = {
    "user_id": "user123",        # Required (or device_id)
    "event_type": "page_view",   # Required
    "time": 1699400000000        # Optional (uses current time if omitted)
}

# 2. Check ID length (min 5 characters)
if len(event["user_id"]) < 5:
    print("Error: user_id must be at least 5 characters")

# 3. Use current timestamp if not provided
import time
event["time"] = int(time.time() * 1000)  # milliseconds

# 4. Check for deduplication (insert_id within 7 days)
# If event has same insert_id within 7 days, it's deduplicated

# 5. Data availability delay (2 hours)
# New data is available in exports after 2 hours
```

### Issue: "Module not found: amplitude"

**Cause:** Driver not installed

**Solution:**

```bash
# Install from source
pip install -e /path/to/amplitude-driver

# Or check installation
python -c "from amplitude import AmplitudeDriver; print('OK')"
```

### Enable Debug Logging

For detailed troubleshooting, enable debug mode:

```python
driver = AmplitudeDriver.from_env(debug=True)

# Now you'll see:
# [DEBUG] POST https://api2.amplitude.com/batch
# [DEBUG] Rate limited. Retrying in 2s (attempt 1/3)
# [DEBUG] POST https://api2.amplitude.com/batch (retry)
```

---

## Examples

Complete examples are available in the `examples/` directory:

- `1_basic_usage.py` - Basic setup and usage
- `2_batch_upload.py` - Batch event upload
- `3_user_properties.py` - Update user properties
- `4_error_handling.py` - Error handling patterns
- `5_export_data.py` - Export historical data

Run examples:

```bash
python examples/1_basic_usage.py
```

---

## Support

### Documentation

- [API Reference](#api-reference) - Complete method documentation
- [Common Patterns](#common-patterns) - Code examples and best practices
- [Troubleshooting](#troubleshooting) - Solutions to common issues

### Reporting Issues

When reporting issues, include:

1. Python version: `python --version`
2. Driver version: `python -c "import amplitude; print(amplitude.__version__)"`
3. Error message and traceback
4. Minimal code to reproduce
5. Environment (OS, network setup)

### Best Practices

- Always use context managers: `with AmplitudeDriver.from_env() as driver:`
- Handle exceptions: catch specific exception types, not base `Exception`
- Enable debug logging during development: `debug=True`
- Use batch operations for high-volume events
- Set appropriate timeout for your use case
- Never hardcode credentials; use environment variables

---

## Version History

### v1.0.0 (2025-11-19)

- ✅ Initial release
- ✅ Batch Event Upload API
- ✅ Identify API (user properties)
- ✅ Export API (historical data)
- ✅ Automatic retry with exponential backoff
- ✅ Comprehensive error handling
- ✅ 100% type hints and documentation

---

## License

[Add your license here - e.g., MIT, Apache 2.0]

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

---

## Acknowledgments

Built following the [Driver Design Specification v2.0](../docs/driver_design_v2.md) with production-ready best practices for reliability, security, and developer experience.

---

**Generated:** 2025-11-19 | **Version:** 1.0.0 | **Status:** Production Ready
