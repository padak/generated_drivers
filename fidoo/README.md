# Fidoo7 Driver

Python driver for Fidoo expense management and prepaid card system API.

## Overview

Fidoo is an enterprise expense management platform providing prepaid card distribution, expense tracking, travel management, and detailed financial reporting. This driver provides complete access to the Fidoo REST API v2.

**Key Capabilities:**
- User account management (create, activate, deactivate, delete)
- Prepaid card operations (view balance, load/unload funds)
- Multi-currency transaction tracking
- Expense recording and reporting
- Travel request and report management
- Configurable settings (cost centers, projects, VAT, accounting categories)
- Batch operations for card funding
- Receipt digitization and download

## Installation

```bash
pip install fidoo7-driver
```

## Quick Start

### Basic Setup

```python
from fidoo7 import Fidoo7Driver

# Option 1: Load from environment (recommended)
client = Fidoo7Driver.from_env()

# Option 2: Explicit credentials
client = Fidoo7Driver(
    base_url="https://api.fidoo.com/v2/",
    api_key="your_api_key_here"
)

# Option 3: Use demo environment
client = Fidoo7Driver(
    base_url="https://api-demo.fidoo.com/v2/",
    api_key="your_demo_api_key"
)
```

### Discovery

```python
# List available endpoints
objects = client.list_objects()
print(objects)
# Output: ['user', 'card', 'transaction', 'expense', 'travel_report', ...]

# Get field schema for an object
fields = client.get_fields("user")
print(fields.keys())
# Output: ['firstName', 'lastName', 'email', 'phone', 'employeeNumber', 'userState', ...]
```

### Query Data

```python
# Simple read
users = client.read("user/get-users", limit=50)
print(f"Found {len(users)} users")

# With pagination
for batch in client.read_batched("user/get-users", batch_size=50):
    for user in batch:
        print(f"{user['firstName']} {user['lastName']}")

# Cleanup
client.close()
```

## Authentication

### Environment Variables (Recommended)

```bash
# Required
export FIDOO_API_KEY="your_api_key_here"

# Optional
export FIDOO_API_URL="https://api.fidoo.com/v2/"      # Default: production
export FIDOO_TIMEOUT="30"                              # Default: 30 seconds
export FIDOO_MAX_RETRIES="3"                           # Default: 3 retries
export FIDOO_DEBUG="true"                              # Default: false
```

Then in code:
```python
client = Fidoo7Driver.from_env()
```

### Getting Your API Key

1. Log in to your Fidoo application
2. Navigate to Settings → API Configuration
3. Click "Generate New API Key"
4. Select permissions (read-only or read-write)
5. Copy and store securely

**Security Notes:**
- Keep API keys private - never commit to version control
- Regenerate keys if compromised
- Use environment variables instead of hardcoding
- Each team member should have their own API key

## API Reference

### Core Methods

#### `list_objects() → List[str]`

Discover all available endpoints/objects.

```python
objects = client.list_objects()
# Returns: ['user', 'card', 'transaction', 'expense', 'travel_report', ...]
```

#### `get_fields(object_name: str) → Dict[str, Any]`

Get complete field schema for an object/endpoint.

```python
fields = client.get_fields("user")
# Returns: {
#     "firstName": {"type": "string", "label": "First Name"},
#     "lastName": {"type": "string", "label": "Last Name"},
#     ...
# }
```

#### `read(query: str, limit: int = None, offset: str = None) → List[Dict]`

Execute a read query and return results.

```python
# Get users
users = client.read("user/get-users", limit=100)

# Get cards with pagination
cards = client.read("card/get-cards", limit=50, offset=next_page_token)

# Get transactions with date filter
transactions = client.read("transaction/get-card-transactions", limit=100)
```

**Parameters:**
- `query` (str): Endpoint path (e.g., "user/get-users", "card/get-cards")
- `limit` (int, optional): Max records returned (default: 50, max: 100)
- `offset` (str, optional): Pagination token for next page

**Returns:** List of records

**Raises:**
- `ObjectNotFoundError`: Endpoint doesn't exist
- `RateLimitError`: Rate limit exceeded
- `TimeoutError`: Request timeout

#### `read_batched(query: str, batch_size: int = 50) → Iterator[List[Dict]]`

Memory-efficient reading for large datasets.

```python
# Process large dataset in batches
total = 0
for batch in client.read_batched("user/get-users", batch_size=100):
    for user in batch:
        # Process user
        pass
    total += len(batch)
    print(f"Processed {total} users...")
```

#### `create(object_name: str, data: Dict) → Dict`

Create a new record.

```python
# Create user
new_user = client.create("user", {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "employeeNumber": "EMP001"
})
print(f"Created user: {new_user['id']}")

# Create cost center
cost_center = client.create("cost_center", {
    "name": "Engineering",
    "description": "Engineering department"
})
```

**Supported object types:** user, cost_center, project, accounting_category, vat_breakdown, account_assignment, vehicle

#### `update(object_name: str, record_id: str, data: Dict) → Dict`

Update an existing record.

```python
# Update user
updated = client.update("user", "user123", {
    "phone": "+1234567890",
    "employeeNumber": "EMP002"
})

# Update cost center
updated = client.update("cost_center", "cc123", {
    "name": "Engineering Team"
})
```

#### `delete(object_name: str, record_id: str) → bool`

Delete a record.

```python
# Delete cost center
success = client.delete("cost_center", "cc123")

# Delete user (must have no roles, tasks, or card holdings)
try:
    success = client.delete("user", "user123")
except ValidationError as e:
    print(f"Cannot delete: {e.message}")
```

**Note:** Some deletions have prerequisites. For example:
- Users cannot be deleted if they have active roles, tasks, or card holdings
- Cost centers cannot be deleted if they're in use

#### `call_endpoint(endpoint: str, method: str, params: Dict, data: Dict) → Dict`

Low-level API access for advanced use cases.

```python
# Call endpoint directly
result = client.call_endpoint(
    endpoint="/v2/user/get-users",
    method="POST",
    data={"limit": 50, "offsetToken": "token123"}
)
```

#### `get_rate_limit_status() → Dict`

Get current rate limit status.

```python
status = client.get_rate_limit_status()
print(f"Rate limit: {status['limit']} requests/day")
# Output: Rate limit: 6000 requests/day
```

### Object Types

#### User
Fields: firstName, lastName, email, phone, employeeNumber, userState (active/deleted/new)

```python
# Get users
users = client.read("user/get-users", limit=100)

# Get by email
user = client.read("user/get-user-by-email", limit=1)

# Create user
user = client.create("user", {"firstName": "Jane", "lastName": "Doe", "email": "jane@example.com"})

# Activate/deactivate
client.read("user/activate-user", limit=1)  # Pass user ID in request body
client.read("user/deactivate-user", limit=1)
```

#### Card
Fields: cardId, status, type (personal/shared), masked_pan, expiration, available_balance

```python
# Get cards
cards = client.read("card/get-cards", limit=50)

# Load funds to single card
load_result = client.read("card/load-card", limit=1)

# Load funds to multiple cards
load_result = client.read("card/load-cards", limit=1)

# Check loading status
status = client.read("card/load-status", limit=1)
```

#### Transaction
Fields: id, cardId, amount, date, description, currency

```python
# Get card transactions
transactions = client.read("transaction/get-card-transactions", limit=100)

# Get cash wallet transactions
cash_txns = client.read("cash-transactions/get-cash-transactions", limit=100)

# Get account transactions
account_txns = client.read("mvc-transaction/get-transactions", limit=100)
```

#### Expense
Fields: id, amount, date, description, status, category, project

```python
# Get expenses
expenses = client.read("expense/get-expenses", limit=100)

# Get expense line items
items = client.read("expense/get-expense-items", limit=100)

# Update expense
updated = client.update("expense", "exp123", {"status": "approved"})
```

#### Settings
- **Cost Centers:** Get, create, update, delete
- **Projects:** Get, create, update, delete
- **Accounting Categories:** Get, create, update, delete
- **VAT Breakdowns:** Get, create, update, delete
- **Account Assignments:** Get, create, update, delete
- **Vehicles:** Get, create, update, delete

```python
# Get cost centers (max 100)
cost_centers = client.read("settings/get-cost-centers", limit=100)

# Create project
project = client.create("project", {"name": "Q4 Marketing"})

# Update VAT breakdown
vat = client.update("vat_breakdown", "vat123", {"rate": 0.21})
```

## Common Patterns

### Pagination for Large Datasets

Use `read_batched()` for memory-efficient processing:

```python
for batch in client.read_batched("user/get-users", batch_size=100):
    print(f"Processing batch of {len(batch)} users")
    # Process batch
```

### Error Handling

```python
from fidoo7 import (
    Fidoo7Driver,
    ObjectNotFoundError,
    RateLimitError,
    AuthenticationError
)

client = Fidoo7Driver.from_env()

try:
    users = client.read("user/get-users")
except ObjectNotFoundError as e:
    print(f"Endpoint not found: {e.message}")
except RateLimitError as e:
    print(f"Rate limited! Retry after {e.details['retry_after']}s")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
finally:
    client.close()
```

### Batch Creation

```python
# Create multiple cost centers
cost_centers = [
    {"name": "Engineering", "description": "Engineering team"},
    {"name": "Sales", "description": "Sales team"},
    {"name": "Marketing", "description": "Marketing team"},
]

created = []
for cc in cost_centers:
    new_cc = client.create("cost_center", cc)
    created.append(new_cc)

print(f"Created {len(created)} cost centers")
```

### Date Range Filtering

```python
# Get expenses for a date range
# Note: Pass date range in request body
expenses = client.read("expense/get-expenses", limit=100)
# Filter in application code or via API filters
```

## Rate Limiting

Fidoo API enforces a limit of **6,000 requests per customer per day**.

The driver automatically:
- Retries failed requests with exponential backoff
- Respects 429 (Too Many Requests) responses
- Limits retries to `max_retries` attempts (default: 3)

```python
# Configure retries
client = Fidoo7Driver.from_env(max_retries=5)  # More aggressive retry

# Check rate limit status
status = client.get_rate_limit_status()
if status["remaining"] and status["remaining"] < 100:
    print("Warning: Low on API quota")
```

## Debug Mode

Enable debug logging to see all API calls:

```python
# Via environment
export FIDOO_DEBUG=true

# Via code
client = Fidoo7Driver.from_env(debug=True)

# All API calls are now logged
users = client.read("user/get-users")
# Output: [DEBUG] POST https://api.fidoo.com/v2/user/get-users
```

## Troubleshooting

### Authentication Failed (401)

```
AuthenticationError: Authentication failed: Unauthorized
```

**Solutions:**
1. Check API key is correct: `echo $FIDOO_API_KEY`
2. Regenerate key in Fidoo app if expired
3. Verify key has required permissions (read-only vs read-write)

### Rate Limit Exceeded (429)

```
RateLimitError: Rate limit exceeded after retries
```

**Solutions:**
1. Reduce request frequency
2. Batch requests into fewer API calls
3. Add delays between requests: `time.sleep(1)`
4. Use `read_batched()` for large datasets
5. Check daily quota usage

### Timeout

```
TimeoutError: Request to /v2/user/get-users timed out after 30 seconds
```

**Solutions:**
1. Increase timeout: `Fidoo7Driver.from_env(timeout=60)`
2. Reduce `limit` parameter (fewer records per request)
3. Check API server status
4. Check network connectivity

### Object Not Found

```
ObjectNotFoundError: Endpoint /v2/user/nonexistent not found
```

**Solutions:**
1. Check endpoint name: `client.list_objects()`
2. Verify correct spelling
3. Check API version compatibility

### Connection Error

```
ConnectionError: Cannot reach Fidoo API
```

**Solutions:**
1. Check internet connectivity
2. Verify API URL: `echo $FIDOO_API_URL`
3. Check Fidoo API server status
4. Try demo environment: `FIDOO_API_URL=https://api-demo.fidoo.com/v2/`

## Production Considerations

### Security
- Never commit API keys to version control
- Use environment variables or secrets management
- Rotate API keys regularly
- Use read-only keys for non-sensitive operations
- Monitor API key usage

### Performance
- Use `read_batched()` for large datasets (memory-efficient)
- Set appropriate `batch_size` (default: 50, max: 100)
- Implement caching for frequently accessed data
- Batch write operations when possible

### Reliability
- Implement exponential backoff for retries
- Add request timeouts (default: 30s)
- Log all errors for debugging
- Monitor rate limit usage
- Plan for API downtime

### Monitoring
```python
import time

start = time.time()
users = client.read("user/get-users")
duration = time.time() - start

print(f"Fetched {len(users)} users in {duration:.2f}s")
```

## Examples

See `examples/` directory for complete runnable scripts:
- `list_all_users.py` - Basic read example
- `pagination_large_dataset.py` - Batched reading
- `error_handling.py` - Exception handling patterns
- `create_and_update.py` - Write operations

## API Documentation

- **Production API:** https://api.fidoo.com/v2/
- **Demo API:** https://api-demo.fidoo.com/v2/
- **Support:** https://www.fidoo.com/support/

## License

MIT

## Version

1.0.0
