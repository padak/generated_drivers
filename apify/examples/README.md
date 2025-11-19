# ApifyDriver Examples

Complete example scripts demonstrating ApifyDriver usage patterns.

## Quick Start

Set up your environment:

```bash
export APIFY_API_TOKEN="your_token_here"
```

Run any example:

```bash
python examples/01_basic_usage.py
```

---

## Examples Overview

### 1. Basic Usage (`01_basic_usage.py`)

**Focus:** Fundamental operations

Learn the basics:
- Initialize driver from environment
- Discover available resources
- Query resources
- Handle basic errors
- Proper cleanup

**Key Concepts:**
- `list_objects()` - What resources are available
- `get_fields()` - Schema for each resource
- `get_capabilities()` - What the driver supports
- `read()` - Basic queries
- `close()` - Resource cleanup

**Run:** `python examples/01_basic_usage.py`

**Time:** ~5-10 seconds

---

### 2. Error Handling (`02_error_handling.py`)

**Focus:** Comprehensive error handling

Learn to handle:
- Authentication errors (invalid token)
- Connection errors (cannot reach API)
- Object not found errors (HTTP 404)
- Field not found errors
- Query syntax errors
- Rate limit errors (HTTP 429)
- Validation errors (invalid parameters)
- Timeout errors
- Error recovery and retry strategies

**Key Concepts:**
- Exception types and when they're raised
- Structured error messages
- Error details for programmatic handling
- Automatic retry with exponential backoff
- Rate limit awareness

**Run:** `python examples/02_error_handling.py`

**Time:** ~10-15 seconds

---

### 3. Pagination (`03_pagination.py`)

**Focus:** Handle large datasets efficiently

Learn pagination patterns:
- Simple pagination with `limit` and `offset`
- Batch processing with `read_batched()`
- Memory-efficient iteration
- Processing large datasets without loading everything into memory
- Rate limit aware pagination
- Finding specific items across pages

**Key Concepts:**
- Offset-based pagination (limit, offset)
- Batch processing for memory efficiency
- Iterator pattern with `read_batched()`
- Page-by-page iteration
- Stopping conditions
- Rate limit handling during iteration

**Run:** `python examples/03_pagination.py`

**Time:** ~10-15 seconds

---

### 4. Debug Mode & Troubleshooting (`04_debug_mode.py`)

**Focus:** Debug and troubleshoot issues

Learn to:
- Enable debug logging to see all API calls
- Inspect driver configuration
- Check driver capabilities
- Monitor rate limit status
- Discover available resources
- Investigate errors
- Configure timeouts and retries
- Check environment setup
- Verify API connectivity

**Key Concepts:**
- Debug logging (`debug=True`)
- Rate limit status monitoring
- Resource discovery
- Error investigation
- Configuration tuning
- Health checks

**Run:** `python examples/04_debug_mode.py`

**Time:** ~10-15 seconds

---

### 5. Advanced Usage (`05_advanced_usage.py`)

**Focus:** Complex patterns and integration

Learn advanced techniques:
- Complex queries with filtering
- Data transformation
- Batch statistics
- Performance optimization
- Custom retry strategies
- Error recovery with fallbacks
- Integration with external systems
- Field mapping between systems
- Resource usage monitoring

**Key Concepts:**
- Filtering and sorting results
- Data transformation pipelines
- Performance tuning
- Custom retry logic
- Fallback strategies
- System integration
- Field mapping
- Usage monitoring

**Run:** `python examples/05_advanced_usage.py`

**Time:** ~15-20 seconds

---

## Common Patterns

### Pattern 1: Simple Query

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()
try:
    actors = client.read("/actors", limit=50)
    for actor in actors:
        print(actor["name"])
finally:
    client.close()
```

### Pattern 2: Process Large Dataset

```python
from apify_driver import ApifyDriver

client = ApifyDriver.from_env()
try:
    for batch in client.read_batched("/actors", batch_size=100):
        print(f"Processing {len(batch)} records...")
        # Process batch here
finally:
    client.close()
```

### Pattern 3: Error Handling

```python
from apify_driver import (
    ApifyDriver,
    ObjectNotFoundError,
    RateLimitError,
)

try:
    client = ApifyDriver.from_env()
    data = client.read("/endpoint")
except ObjectNotFoundError as e:
    print(f"Not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.details['retry_after']}s")
finally:
    client.close()
```

### Pattern 4: Debug Issues

```python
from apify_driver import ApifyDriver

# Enable debug logging
client = ApifyDriver.from_env(debug=True)
try:
    data = client.read("/actors")  # All calls logged with [DEBUG]
finally:
    client.close()
```

---

## Running All Examples

Run all examples in sequence:

```bash
# Create a script that runs all examples
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
    echo ""
done
```

Or run specific examples:

```bash
python examples/01_basic_usage.py
python examples/02_error_handling.py
python examples/03_pagination.py
python examples/04_debug_mode.py
python examples/05_advanced_usage.py
```

---

## Output Examples

### 01_basic_usage.py Output

```
======================================================================
EXAMPLE 1: Basic ApifyDriver Usage
======================================================================

1. DISCOVERY - What resources are available?
----------------------------------------------------------------------
Available resources (9):
  • actors
  • runs
  • datasets
  • key-value-stores
  • ...

2. SCHEMA - What fields does each resource have?
----------------------------------------------------------------------
Actor fields (15):
  • id: string
  • name: string
  • ...
```

### 02_error_handling.py Output

```
1. AUTHENTICATION ERRORS
----------------------------------------------------------------------
✓ Authentication successful

2. OBJECT NOT FOUND
----------------------------------------------------------------------
❌ Resource not found: Resource not found: /invalid-endpoint
   Endpoint: /invalid-endpoint
   Solution: Use client.list_objects() to see available resources
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'apify_driver'"

Solution: Install the driver first

```bash
pip install generated_drivers/apify
# or
pip install -e generated_drivers/apify
```

### "AuthenticationError: Missing Apify API token"

Solution: Set environment variable

```bash
export APIFY_API_TOKEN="your_token_here"
```

Get token from: https://console.apify.com/settings/integrations

### "ConnectionError: Cannot reach Apify API"

Solution: Check network connectivity

```bash
# Verify API is reachable
curl https://api.apify.com/v2/acts -H "Authorization: Bearer your_token"
```

### "RateLimitError: Rate limit exceeded"

Solution: The driver automatically retries with backoff. If still rate limited:
- Use smaller batch sizes
- Add delays between requests
- Wait for rate limit window to reset

### "ObjectNotFoundError: Resource not found"

Solution: Verify resource exists

```python
# List available resources
resources = client.list_objects()
print(resources)
```

---

## Performance Tips

### For Large Datasets

✅ Use `read_batched()` for memory efficiency:
```python
for batch in client.read_batched("/actors", batch_size=100):
    process(batch)
```

❌ Avoid loading everything at once:
```python
all_data = client.read("/actors", limit=1000000)  # Bad!
```

### For Rate Limiting

✅ Default retry is automatic:
```python
# Automatically retries on HTTP 429
data = client.read("/actors")
```

✅ Add delays between batches:
```python
for batch in client.read_batched("/actors", batch_size=50):
    process(batch)
    time.sleep(0.1)  # Small delay
```

### For Debugging

✅ Enable debug mode:
```python
client = ApifyDriver.from_env(debug=True)
```

✅ Check rate limit status:
```python
status = client.get_rate_limit_status()
if status["remaining"] < 100:
    print("Warning: Few requests left")
```

---

## Next Steps

1. **Run all examples** to understand the API
2. **Read the README** in the driver package for API reference
3. **Build your script** using example patterns
4. **Enable debug mode** if you hit issues
5. **Check troubleshooting** for solutions

---

## Documentation Links

- **Driver README:** `../README.md`
- **API Reference:** https://docs.apify.com/api/v2
- **Python Client Docs:** https://docs.apify.com/api/client/python
- **Support:** https://console.apify.com

---

## License

MIT - See LICENSE file in driver package

---

**Generated:** 2025-11-19
**ApifyDriver Version:** 1.0.0
**Status:** Ready for Production
