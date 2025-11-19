# PostHog Driver - Example Scripts

This directory contains comprehensive example scripts demonstrating all features of the PostHog Python driver.

---

## Quick Navigation

| Example | Purpose | Duration | Difficulty |
|---------|---------|----------|------------|
| [`basic_usage.py`](#basic-usage) | Get started with the driver | 5 min | ⭐ Beginner |
| [`error_handling.py`](#error-handling) | Proper error handling patterns | 10 min | ⭐⭐ Intermediate |
| [`pagination.py`](#pagination) | Handle large datasets efficiently | 15 min | ⭐⭐ Intermediate |
| [`write_operations.py`](#write-operations) | CRUD operations | 15 min | ⭐⭐ Intermediate |
| [`advanced_usage.py`](#advanced-usage) | Complex patterns and optimization | 20 min | ⭐⭐⭐ Advanced |

---

## Prerequisites

All examples require:

1. **Python 3.8+**
2. **PostHog API Key** (set `POSTHOG_API_KEY` environment variable)
3. **PostHog Driver** installed

### Setup

```bash
# Set your API key
export POSTHOG_API_KEY=your_personal_api_key

# Optional: Set API URL (defaults to US cloud)
export POSTHOG_API_URL=https://app.posthog.com/api

# Optional: Set project ID
export POSTHOG_PROJECT_ID=your_project_id

# Run any example
python basic_usage.py
```

---

## Examples

### Basic Usage

**File:** `basic_usage.py`

Demonstrates:
- Initialize driver from environment
- List available resources
- Get resource schema
- Read data
- Cleanup

**Key Concepts:**
```python
# Initialize
driver = PostHogDriver.from_env()

# Discover
objects = driver.list_objects()
fields = driver.get_fields("dashboards")

# Read
results = driver.read("/dashboards", limit=50)

# Cleanup
driver.close()
```

**When to use:** Start here! This is the foundation for all other examples.

**Output:**
```
1. Initializing driver from environment...
   ✓ Driver initialized successfully

2. Listing available resources...
   Available resources (10):
     1. batch_exports
     2. dashboards
     ...

3. Getting field schema for 'dashboards'...
   Fields (15):
     - id: string (optional)
     - name: string (required)
     ...
```

---

### Error Handling

**File:** `error_handling.py`

Demonstrates:
- Authentication error handling
- Connection error handling
- Resource not found errors
- Validation errors
- Rate limit errors
- Generic error handling
- Best practice patterns

**Key Concepts:**
```python
# Catch specific errors
try:
    driver.read("/dashboards", limit=101)  # Exceeds max
except ValidationError as e:
    print(f"Fix: {e.details.get('suggestion')}")

# Catch any driver error
try:
    driver = PostHogDriver.from_env()
except DriverError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")

# Use try/finally for cleanup
try:
    results = driver.read("/dashboards")
finally:
    driver.close()
```

**When to use:** Learn proper error handling before writing production code.

**Error Types Covered:**
- `AuthenticationError` - Invalid credentials
- `ConnectionError` - Cannot reach API
- `ObjectNotFoundError` - Resource not found
- `ValidationError` - Data validation failed
- `RateLimitError` - Rate limit exceeded

---

### Pagination

**File:** `pagination.py`

Demonstrates:
- Manual pagination (limit/offset)
- Automatic batched reading
- Memory-efficient processing
- Filtering during pagination
- Aggregation during batch processing
- Rate limit aware pagination

**Key Concepts:**
```python
# Manual pagination
offset = 0
while True:
    data = driver.read("/dashboards", limit=50, offset=offset)
    if not data:
        break
    offset += 50

# Automatic batched reading (recommended!)
for batch in driver.read_batched("/events", batch_size=100):
    process_batch(batch)

# Aggregate during processing
event_counts = {}
for batch in driver.read_batched("/events", batch_size=100):
    for event in batch:
        event_type = event.get("event")
        event_counts[event_type] += 1
```

**When to use:** When processing more than a few dozen records.

**Performance Tips:**
- Use `read_batched()` instead of `read()` with large limits
- Default batch size 100 is good, adjust if needed
- Add delays between requests to respect rate limits
- Process data in batches rather than storing everything in memory

---

### Write Operations

**File:** `write_operations.py`

Demonstrates:
- Create resources
- Read resources
- Update resources
- Delete resources
- Batch create operations
- Complete CRUD workflow
- Error handling in write operations

**Key Concepts:**
```python
# Create
dashboard = driver.create("dashboards", {
    "name": "My Dashboard",
    "description": "Description"
})

# Read
dashboards = driver.read("/dashboards", limit=5)

# Update
updated = driver.update("dashboards", dashboard_id, {
    "name": "Updated Name"
})

# Delete (soft delete)
success = driver.delete("dashboards", dashboard_id)

# Batch operations
for dashboard_data in dashboard_list:
    try:
        created = driver.create("dashboards", dashboard_data)
    except ValidationError:
        # Continue with next item
        pass
```

**When to use:** When you need to create, modify, or delete data.

**Important Notes:**
- Always check required fields before creating
- Use try/except for batch operations
- PostHog uses soft delete (resources are hidden, not removed)
- Update operations use PATCH (partial update)

---

### Advanced Usage

**File:** `advanced_usage.py`

Demonstrates:
- Combined operations (read → filter → create)
- Advanced filtering and aggregation
- Performance optimization
- Debug mode for troubleshooting
- Custom endpoint calls
- Advanced error recovery with retries
- Monitoring and logging patterns

**Key Concepts:**
```python
# Combined operations
dashboards = driver.read("/dashboards", limit=20)
filtered = [d for d in dashboards if "test" not in d.get("name", "")]

# Advanced filtering during batch processing
event_stats = {}
for batch in driver.read_batched("/events", batch_size=100):
    for event in batch:
        event_type = event.get("event")
        event_stats[event_type] = event_stats.get(event_type, 0) + 1

# Debug mode
driver = PostHogDriver.from_env(debug=True)
results = driver.read("/dashboards")  # Shows detailed logs

# Custom endpoint call
result = driver.call_endpoint(
    endpoint="/dashboards",
    method="GET",
    params={"limit": 5}
)

# Exponential backoff retry
for attempt in range(3):
    try:
        data = driver.read("/dashboards")
        break
    except RateLimitError as e:
        if attempt < 2:
            delay = 2 ** attempt
            time.sleep(delay)
```

**When to use:** When working with complex operations or optimizing performance.

**Advanced Patterns:**
- Exponential backoff for rate limit recovery
- Graceful degradation when operations fail
- Monitoring and metrics collection
- Debug mode for troubleshooting
- Custom endpoint calls for non-standard operations

---

## Running Examples

### Run a Single Example

```bash
python basic_usage.py
```

### Run All Examples

```bash
# Create a simple test script
for example in *.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```

### Run with Debug Output

```bash
# Add debug flag to driver initialization in example
export DEBUG=true
python basic_usage.py
```

---

## Common Patterns

### The Standard Pattern

This is the pattern used in all examples:

```python
from posthog_driver import PostHogDriver, DriverError

# Initialize
driver = PostHogDriver.from_env()

try:
    # Your operations here
    results = driver.read("/dashboards")

except DriverError as e:
    # Handle errors
    print(f"Error: {e.message}")

finally:
    # Always cleanup
    driver.close()
```

### Error Handling Pattern

```python
from posthog_driver import (
    PostHogDriver,
    ValidationError,
    ObjectNotFoundError,
    RateLimitError,
)

try:
    driver = PostHogDriver.from_env()
    results = driver.read("/dashboards")

except ValidationError as e:
    # Invalid input
    print(f"Validation error: {e.message}")

except ObjectNotFoundError as e:
    # Resource not found
    print(f"Not found: {e.message}")

except RateLimitError as e:
    # Rate limit - implement retry logic
    retry_after = e.details['retry_after']
    print(f"Rate limited, retry after {retry_after}s")

except Exception as e:
    # Unexpected error
    print(f"Unexpected error: {e}")

finally:
    driver.close()
```

### Batch Processing Pattern

```python
driver = PostHogDriver.from_env()

try:
    for batch in driver.read_batched("/events", batch_size=100):
        # Process batch
        for event in batch:
            process_event(event)

        # Optional: Check rate limits
        status = driver.get_rate_limit_status()
        if status["remaining"] < 10:
            print("Warning: Running low on API quota")

finally:
    driver.close()
```

---

## Troubleshooting

### Missing API Key

```
Error: Missing PostHog API key. Set POSTHOG_API_KEY environment variable.
```

**Solution:**
```bash
export POSTHOG_API_KEY=your_personal_api_key
```

### Cannot Reach API

```
Error: Cannot reach PostHog API at https://app.posthog.com/api
```

**Solutions:**
1. Check internet connection
2. Verify API URL is correct
3. Try with explicit URL:
   ```python
   driver = PostHogDriver(
       api_url="https://app.posthog.com/api",
       api_key="your_key"
   )
   ```

### Rate Limit Exceeded

```
Error: API rate limit exceeded (480 req/min)
```

**Solutions:**
1. Reduce batch size
2. Add delays between requests
3. Use `read_batched()` for large datasets
4. Implement retry logic with exponential backoff

### Resource Not Found

```
Error: Object 'invalid_name' not found in PostHog API
```

**Solution:**
```python
# Check available resources
objects = driver.list_objects()
print(objects)
```

---

## Performance Tips

1. **Use `read_batched()` for large datasets**
   - Memory efficient
   - Automatic pagination

2. **Optimize batch size**
   - Default 100 is good
   - Reduce if rate limited
   - Increase if network latency is high

3. **Add rate-limit awareness**
   - Check `get_rate_limit_status()`
   - Add delays between requests
   - Implement retry logic

4. **Cache schema information**
   - Call `list_objects()` once
   - Call `get_fields()` once per resource type
   - Cache results locally

5. **Use debug mode for development**
   ```python
   driver = PostHogDriver.from_env(debug=True)
   ```

---

## Learning Path

Follow this path to learn the driver:

1. **Start:** `basic_usage.py`
   - Understand basic operations
   - Learn initialization and cleanup

2. **Practice:** `error_handling.py`
   - Learn proper error handling
   - Understand exception types

3. **Scale:** `pagination.py`
   - Process large datasets
   - Understand rate limits

4. **Modify:** `write_operations.py`
   - Create, update, delete operations
   - CRUD workflow

5. **Optimize:** `advanced_usage.py`
   - Complex operations
   - Performance patterns
   - Monitoring

---

## Additional Resources

- **README:** See `../README.md` for full documentation
- **API Reference:** See `../README.md` Section 7
- **Troubleshooting:** See `../README.md` Section 9
- **Source Code:** See `../client.py` for implementation details

---

## Contributing Examples

To contribute new examples:

1. Follow the existing pattern
2. Include comprehensive docstrings
3. Add error handling
4. Include cleanup (finally block)
5. Add explanatory print statements
6. Document in this README

---

**Last Updated:** 2025-11-19
**Status:** ✅ Production Ready
