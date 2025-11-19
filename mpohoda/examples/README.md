# MPohodaDriver Examples

Comprehensive examples demonstrating all usage patterns for the mPOHODA driver.

## Quick Navigation

| Example | Purpose | Complexity |
|---------|---------|-----------|
| **basic_usage.py** | Simple read operations | Beginner |
| **error_handling.py** | Exception handling patterns | Beginner |
| **pagination.py** | Large dataset handling | Intermediate |
| **write_operations.py** | Creating records | Intermediate |
| **advanced_usage.py** | Production patterns | Advanced |

---

## Example 1: Basic Usage

**File:** `basic_usage.py`

Demonstrates the most common usage pattern:
- Initialize driver from environment
- Discover available objects
- Read records
- Process results
- Cleanup

**Key learnings:**
- `MPohodaDriver.from_env()` - Load from environment variables
- `list_objects()` - Discover available objects
- `read()` - Basic read operation
- `get_fields()` - Explore object schema
- `driver.close()` - Cleanup

**Run:**
```bash
export MPOHODA_API_KEY=your_key
python examples/basic_usage.py
```

---

## Example 2: Error Handling

**File:** `error_handling.py`

Demonstrates how to handle different error scenarios:
- Authentication errors (invalid credentials)
- Object not found (wrong object name)
- Validation errors (invalid parameters)
- Rate limit errors (too many requests)
- Timeout errors (request timeout)
- Connection errors (network issues)
- Graceful degradation pattern

**Key learnings:**
- Exception types and when they occur
- How to access error details
- Recovery strategies for each error type
- Production error handling pattern

**Exceptions covered:**
```
AuthenticationError    (401/403) - Invalid credentials
ConnectionError        (Network) - Cannot reach API
ObjectNotFoundError    (404)     - Object doesn't exist
ValidationError        (422)     - Invalid parameters
RateLimitError         (429)     - Rate limit exceeded
TimeoutError           (-)       - Request timeout
```

**Run:**
```bash
export MPOHODA_API_KEY=your_key
python examples/error_handling.py
```

---

## Example 3: Pagination

**File:** `pagination.py`

Demonstrates pagination strategies for large datasets:

### Offset-Based Pagination
Traditional approach using page numbers.
```python
for page in range(1, 100):
    records = driver.read("Activities", page_number=page, page_size=50)
```

**When to use:**
- Small to medium datasets
- UI pagination with specific page numbers
- When you need to show "Page X of Y"

### Keyset-Based Pagination (Recommended)
Efficient cursor-based pagination.
```python
for batch in driver.read_batched("Activities", batch_size=50):
    process_batch(batch)
```

**When to use:**
- Large datasets
- Memory efficiency is important
- Background jobs and data exports
- When handling concurrent modifications

**Key learnings:**
- Difference between offset and keyset pagination
- When to use each approach
- Filtering with ModifiedSince
- Gathering statistics during pagination

**Run:**
```bash
export MPOHODA_API_KEY=your_key
python examples/pagination.py
```

---

## Example 4: Write Operations

**File:** `write_operations.py`

Demonstrates creating records (write operations):
- Create single record
- Create multiple records
- Error handling for create
- Optional fields
- Unsupported operations (update, delete)

**Supported operations:**
- ✅ `create()` - Create new records (POST)

**Not supported:**
- ❌ `update()` - Returns 405 Method Not Allowed
- ❌ `delete()` - Returns 405 Method Not Allowed

**Key learnings:**
- How to prepare data for create operations
- Handling validation errors
- Batch creation pattern
- API limitations

**Example:**
```python
partner = driver.create("BusinessPartners", {
    "name": "Company Name",
    "taxNumber": "CZ12345678",
    "identificationNumber": "12345678",
    "addresses": [...]
})
```

**Run:**
```bash
export MPOHODA_API_KEY=your_key
python examples/write_operations.py
```

---

## Example 5: Advanced Usage

**File:** `advanced_usage.py`

Production-ready patterns for complex scenarios:

### 1. Multi-Object Synchronization
- Synchronize multiple objects
- Track progress and statistics
- Error handling across objects

### 2. Data Transformation Pipeline
- Read original data
- Transform for processing
- Export results

### 3. Retry Pattern
- Handle rate limiting with retries
- Exponential backoff
- Max retry limit

### 4. Field Discovery
- Explore all available objects
- Discover fields for each object
- Build dynamic forms or schemas

### 5. Capabilities-Based Logic
- Check what operations are supported
- Conditional logic based on capabilities
- Handle API limitations gracefully

**Key learnings:**
- Context managers for resource management
- Logging and monitoring
- Statistics tracking
- Production resilience patterns
- Dynamic schema discovery

**Key class:**
```python
class MPohodaSync:
    """Advanced synchronization client with:
    - Multi-object data retrieval
    - Resilience and retry logic
    - Data transformation
    - Progress tracking
    - Detailed logging
    """
```

**Run:**
```bash
export MPOHODA_API_KEY=your_key
python examples/advanced_usage.py
```

---

## Common Patterns

### Pattern 1: Simple Read
```python
driver = MPohodaDriver.from_env()
try:
    records = driver.read("Activities")
finally:
    driver.close()
```

### Pattern 2: Batch Processing
```python
driver = MPohodaDriver.from_env()
try:
    for batch in driver.read_batched("Activities"):
        process_batch(batch)
finally:
    driver.close()
```

### Pattern 3: Error Handling
```python
from mpohoda import MPohodaDriver, ObjectNotFoundError

try:
    driver = MPohodaDriver.from_env()
    records = driver.read("Activities")
except ObjectNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Available: {e.details['available']}")
```

### Pattern 4: With Context Manager
```python
from advanced_usage import MPohodaSync

with MPohodaSync() as sync:
    records = sync.sync_object("Activities")
```

---

## Environment Variables

Required (at least one):
- `MPOHODA_API_KEY` - API key for authentication
- `MPOHODA_CLIENT_ID` + `MPOHODA_CLIENT_SECRET` - OAuth2

Optional:
- `MPOHODA_BASE_URL` - Custom API URL
- `MPOHODA_ACCESS_TOKEN` - Pre-obtained OAuth2 token

---

## Available Objects

All examples support these 10 objects:
- Activities
- BusinessPartners
- Banks
- BankAccounts
- CashRegisters
- Centres
- Establishments
- Countries
- Currencies
- CityPostCodes

---

## Running Examples

### Setup
```bash
# Set API credentials
export MPOHODA_API_KEY=your_key

# Or OAuth2
export MPOHODA_CLIENT_ID=your_id
export MPOHODA_CLIENT_SECRET=your_secret
```

### Run Single Example
```bash
python examples/basic_usage.py
python examples/error_handling.py
python examples/pagination.py
python examples/write_operations.py
python examples/advanced_usage.py
```

### Run All Examples
```bash
for example in examples/*.py; do
    echo "Running $example..."
    python "$example"
done
```

---

## Learning Path

**For beginners:**
1. Start with `basic_usage.py`
2. Learn error handling with `error_handling.py`
3. Explore pagination with `pagination.py`

**For intermediate users:**
1. Study write operations in `write_operations.py`
2. Understand advanced patterns in `advanced_usage.py`

**For production use:**
1. Review `advanced_usage.py` for best practices
2. Use context managers for resource management
3. Implement proper logging and error handling
4. Test with your actual data

---

## Tips and Best Practices

### 1. Always Use Context Managers
```python
with MPohodaDriver.from_env() as driver:
    records = driver.read("Activities")
# Driver automatically closed
```

### 2. Handle Rate Limits Gracefully
```python
try:
    driver.read("Activities")
except RateLimitError as e:
    wait_time = e.details["retry_after"]
    time.sleep(wait_time)
```

### 3. Log Important Operations
```python
logger.info(f"Reading {object_name}...")
records = driver.read(object_name)
logger.info(f"Retrieved {len(records)} records")
```

### 4. Validate Before Processing
```python
if not records:
    logger.warning("No records found")
    return

for record in records:
    process(record)
```

### 5. Batch Large Operations
```python
for batch in driver.read_batched("Activities", batch_size=50):
    process_batch(batch)  # Process in chunks
```

---

## Troubleshooting

**"Missing authentication credentials"**
```bash
export MPOHODA_API_KEY=your_key
```

**"Object not found"**
```python
objects = driver.list_objects()  # See available objects
```

**"page_size cannot exceed 50"**
```python
driver.read("Activities", page_size=50)  # Use 50 or less
```

**"Rate limit exceeded"**
- Driver automatically retries
- If still failing, wait or reduce batch size

---

## Additional Resources

- **API Documentation**: https://api.mpohoda.cz/doc
- **Swagger UI**: https://api.mpohoda.cz/swagger/index.html
- **ReDoc**: https://api.mpohoda.cz/redoc
- **Driver README**: See parent directory

---

## Contributing

To add new examples:
1. Follow the naming convention: `{purpose}.py`
2. Include comprehensive docstrings
3. Add to this README
4. Test with real credentials

---

**Version:** 1.0.0
**Last Updated:** 2025-11-19
