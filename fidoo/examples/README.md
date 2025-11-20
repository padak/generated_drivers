# Fidoo8Driver Examples

Comprehensive examples demonstrating all features of the Fidoo8Driver.

## Quick Start

### Prerequisites

Set up your API credentials:

```bash
export FIDOO_API_KEY="your_api_key_here"
export FIDOO_BASE_URL="https://api.fidoo.com/v2"  # Or demo: https://api-demo.fidoo.com/v2
```

### Running Examples

```bash
# Navigate to examples directory
cd examples/

# Run any example
python basic_usage.py
python error_handling.py
python pagination.py
python write_operations.py
python advanced_usage.py
```

## Examples Overview

### 1. basic_usage.py - Getting Started

**Topics:**
- Initializing the driver
- Discovering available objects
- Inspecting object schemas
- Simple queries
- Checking driver capabilities

**Key Methods:**
- `list_objects()` - Get available objects
- `get_fields()` - Get field schema
- `get_capabilities()` - Check driver capabilities
- `read()` - Query objects

**Use When:**
- Learning the driver
- Understanding data structure
- Planning queries
- Checking what objects are available

**Run:**
```bash
python basic_usage.py
```

**Output:**
```
STEP 1: Discover Available Objects
Available objects in Fidoo API (17 total):
  1. User
  2. Card
  ...

STEP 2: Inspect Object Schema
User object has 14 fields:
  userId                  string      Unique user identifier (UUID)
  ...

STEP 3: Query Users
Fetched 10 users:
  1. John Doe (john@example.com)
  ...
```

---

### 2. error_handling.py - Exception Management

**Topics:**
- Handling missing objects (ObjectNotFoundError)
- Handling validation errors (ValidationError)
- Handling rate limits (RateLimitError)
- Handling authentication errors (AuthenticationError)
- Handling connection errors (ConnectionError)
- Retry strategies
- Exception hierarchy

**Key Methods:**
- Exception handling with try/except
- Error details inspection
- Retry patterns
- Safe query functions

**Exception Types:**
- `ObjectNotFoundError` - Invalid object name
- `ValidationError` - Invalid parameters
- `RateLimitError` - Rate limit exceeded
- `AuthenticationError` - Auth failed
- `ConnectionError` - Network error
- `TimeoutError` - Request timeout

**Use When:**
- Building robust applications
- Implementing retry logic
- Debugging API issues
- Understanding error responses

**Run:**
```bash
python error_handling.py
```

**Output:**
```
EXAMPLE 1: Handle Missing Object
Attempting to query non-existent object 'InvalidObject'...

❌ ObjectNotFoundError
   Message: Object 'InvalidObject' not found in Fidoo API
   Available objects: ['User', 'Card', 'Transaction', ...]

✅ Retrying with valid object 'User'...
   Success! Got 5 users
```

---

### 3. pagination.py - Large Dataset Processing

**Topics:**
- Cursor-based pagination
- Batch processing
- Memory-efficient iteration
- Progress tracking
- Combining results from multiple batches
- Performance optimization

**Key Methods:**
- `read_batched()` - Iterator for memory-efficient processing
- `read()` - Get all results at once (returns complete set)
- Manual batch collection

**Use When:**
- Processing large datasets (1000+ records)
- Memory-constrained environments
- Aggregating data across batches
- Building real-time processing pipelines

**Run:**
```bash
python pagination.py
```

**Output:**
```
EXAMPLE 1: Simple Batch Processing
Processing users in batches of 50...

Batch 1: 50 users
Total so far: 50
  1. John Doe
  2. Jane Smith
  3. Bob Johnson
  ... and 47 more

[Demo: stopping after 3 batches]

✅ Processed 3 batches (150 total users)
```

---

### 4. write_operations.py - Create, Update, Delete

**Topics:**
- Creating new records
- Updating existing records
- Deleting records
- Handling validation errors
- Verifying results
- Batch creation patterns
- Best practices for write operations

**Key Methods:**
- `create()` - Create new records
- `update()` - Update existing records
- `delete()` - Delete records
- `read()` - Verify operations

**Supported Objects:**
- User (create, delete)
- Expense (update)
- Others (depends on API permissions)

**Use When:**
- Automating data entry
- Bulk importing data
- Updating records
- Data cleanup and maintenance

**Run:**
```bash
python write_operations.py
```

**Output:**
```
EXAMPLE 1: Create a New User
Creating new user...
User data: {'firstName': 'John', 'lastName': 'Doe', ...}

✅ User created successfully!
   User ID: 30dcca40-9858-4139-9230-bb86d97cf64e
   Name: John Doe
   Email: john.doe@example.com
```

**⚠️ WARNING:** This example modifies data! Use with caution on production.

---

### 5. advanced_usage.py - Complex Operations

**Topics:**
- Multi-object queries and correlation
- Data aggregation and analytics
- Time-series analysis
- Custom filtering and transformation
- Resilient data collection
- Performance monitoring
- Complex error handling

**Patterns:**
- Multi-object analysis
- Aggregations (grouping, counting)
- Statistics calculation
- Resilient queries with retry
- Memory-efficient processing
- Performance monitoring

**Use When:**
- Building analytics dashboards
- Automating complex workflows
- Correlating data across objects
- Optimizing performance
- Building production applications

**Run:**
```bash
python advanced_usage.py
```

**Output:**
```
EXAMPLE 1: Multi-Object Analysis
Analyzing relationship between users and cards...
  Loaded 50 users
  Loaded 50 cards

Card ownership analysis:
  Users with cards: 42
  Users without cards: 8

Top card holder:
  John Smith
  Cards: 3
    1. JOHN SMITH (active)
    2. JOHN SMITH (active)
    3. JOHN SMITH (soft-blocked)
```

---

## Pattern Reference

### Query Pattern

```python
from fidoo8 import Fidoo8Driver

client = Fidoo8Driver.from_env()
try:
    # Query object
    results = client.read("User", limit=50)

    # Process results
    for record in results:
        print(record)
finally:
    client.close()
```

### Pagination Pattern

```python
# Process large datasets efficiently
for batch in client.read_batched("User", batch_size=50):
    for record in batch:
        process(record)
```

### Error Handling Pattern

```python
from fidoo8.exceptions import RateLimitError, ObjectNotFoundError

try:
    results = client.read("User")
except ObjectNotFoundError as e:
    print(f"Object not found: {e.details['available']}")
except RateLimitError as e:
    wait_time = e.details['retry_after']
    time.sleep(wait_time)
    results = client.read("User")
```

### Create Pattern

```python
new_record = client.create("User", {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
})
print(f"Created: {new_record['userId']}")
```

### Update Pattern

```python
updated = client.update("Expense", expense_id, {
    "name": "Updated Name",
    "state": "approve"
})
print(f"Updated: {updated['expenseId']}")
```

### Delete Pattern

```python
success = client.delete("User", user_id)
print(f"Deleted: {success}")
```

---

## Common Tasks

### Get All Users

```python
users = client.read("User", limit=100)
```

### Process Large User Dataset

```python
for batch in client.read_batched("User", batch_size=50):
    process_batch(batch)
```

### Create Multiple Users

```python
users_data = [
    {"firstName": "A", "lastName": "B", "email": "a@example.com"},
    {"firstName": "C", "lastName": "D", "email": "c@example.com"},
]

for data in users_data:
    new_user = client.create("User", data)
    print(f"Created: {new_user['userId']}")
```

### Filter Records

```python
users = client.read("User", limit=100)
active_users = [u for u in users if u.get('userState') == 'active']
```

### Aggregate Data

```python
expenses = client.read("Expense", limit=100)

total = sum(e.get('amountCzk', 0) for e in expenses)
by_state = {}
for expense in expenses:
    state = expense.get('state')
    by_state[state] = by_state.get(state, 0) + 1
```

### Safe Retry Query

```python
def safe_query(client, obj, limit=50, retries=3):
    for attempt in range(retries):
        try:
            return client.read(obj, limit=limit)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

---

## Best Practices

### 1. Always Use Context Management

```python
# ✓ Good
try:
    client = Fidoo8Driver.from_env()
    results = client.read("User")
finally:
    client.close()

# ✗ Bad
client = Fidoo8Driver.from_env()
results = client.read("User")
# Client not closed!
```

### 2. Handle Errors Appropriately

```python
# ✓ Good
try:
    results = client.read(object_name)
except ObjectNotFoundError:
    # Get available objects and retry
    print(client.list_objects())
except RateLimitError as e:
    # Wait and retry
    time.sleep(e.details['retry_after'])

# ✗ Bad
results = client.read(object_name)  # No error handling
```

### 3. Use Batched Reading for Large Datasets

```python
# ✓ Good - Memory efficient
for batch in client.read_batched("User", batch_size=50):
    process_batch(batch)

# ✗ Bad - Loads everything into memory
all_users = client.read("User", limit=10000)
for user in all_users:
    process(user)
```

### 4. Validate Data Before Writing

```python
# ✓ Good
user_data = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com"
}
if all(user_data.values()):
    new_user = client.create("User", user_data)

# ✗ Bad
client.create("User", {"firstName": "John"})  # Missing required fields
```

### 5. Test with Demo API First

```bash
# ✓ Good - Test in safe environment
export FIDOO_BASE_URL="https://api-demo.fidoo.com/v2"
python write_operations.py

# ✗ Bad - Direct production use
export FIDOO_BASE_URL="https://api.fidoo.com/v2"
python write_operations.py
```

---

## Troubleshooting

### "Missing Fidoo API key"

```bash
# Set required environment variable
export FIDOO_API_KEY="your_api_key_here"
```

### "Object 'Users' not found"

```python
# Object names are case-sensitive
client.read("User")  # ✓ Correct
client.read("Users")  # ✗ Wrong
client.read("USERS")  # ✗ Wrong

# List available objects
print(client.list_objects())
```

### "Rate limited!"

```python
# Use safe retry pattern
try:
    results = client.read("User")
except RateLimitError as e:
    wait_time = e.details['retry_after']
    time.sleep(wait_time)
    results = client.read("User")
```

### Timeout Errors

```python
# Increase timeout
client = Fidoo8Driver(timeout=60)

# Or reduce batch size
results = client.read("User", limit=10)
```

---

## Next Steps

1. **Start with:** `basic_usage.py` - Learn the basics
2. **Then try:** `pagination.py` - Handle larger datasets
3. **Add error handling:** `error_handling.py` - Make it robust
4. **Create data:** `write_operations.py` - Automate data entry
5. **Advanced:** `advanced_usage.py` - Complex workflows

## Support

- **Documentation:** See README.md
- **API Reference:** https://www.fidoo.com/support/expense-management-en/it-specialist/specifications-api/
- **Test Data:** Request from info@fidoo.com
- **Issues:** Check error messages and troubleshooting section

---

**Ready to use Fidoo8Driver!** Start with `basic_usage.py` now.
