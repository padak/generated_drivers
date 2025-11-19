# Stripe API Driver

A production-ready Python driver for the [Stripe API](https://docs.stripe.com/api).

Provides complete CRUD operations for Stripe resources with automatic rate limiting, error handling, and cursor-based pagination.

## Features

- ✅ **Bearer Token Authentication** - Secure API key authentication
- ✅ **Cursor-Based Pagination** - Efficient pagination with max 100 records per page
- ✅ **Automatic Rate Limiting** - Exponential backoff retry strategy
- ✅ **Comprehensive Error Handling** - Structured exceptions with actionable messages
- ✅ **30+ Resource Types** - Products, Customers, Invoices, Payment Intents, Quotes, and more
- ✅ **Full CRUD Support** - Create, read, update, and delete operations
- ✅ **Debug Mode** - Detailed logging for troubleshooting
- ✅ **Connection Pooling** - Automatic HTTP session management

## Installation

```bash
pip install stripe-driver
```

Or install from source:

```bash
git clone https://github.com/your-repo/stripe-driver.git
cd stripe-driver
pip install -e .
```

## Quick Start

### Basic Usage

```python
from stripe_driver import StripeDriver

# Create driver from environment variables
client = StripeDriver.from_env()

# Query products
products = client.read("products", limit=10)
for product in products:
    print(f"Product: {product['name']} ({product['id']})")

# Create a product
product = client.create("products", {
    "name": "My Product",
    "type": "service",
    "description": "A great product"
})
print(f"Created product: {product['id']}")

# Update a product
updated = client.update("products", "prod_123", {
    "name": "Updated Product Name"
})

# Delete a product
client.delete("products", "prod_123")

# Cleanup
client.close()
```

### With Explicit Credentials

```python
client = StripeDriver(
    api_key="sk_test_...",
    base_url="https://api.stripe.com",
    timeout=60,
    max_retries=3,
    debug=True  # Enable debug logging
)
```

### Pagination for Large Datasets

```python
# Batch processing with automatic pagination
for batch in client.read_batched("products", batch_size=100):
    process_batch(batch)
    print(f"Processed {len(batch)} products")
```

### Error Handling

```python
from stripe_driver import (
    StripeDriver,
    ObjectNotFoundError,
    RateLimitError,
    ValidationError
)

client = StripeDriver.from_env()

try:
    products = client.read("products", limit=10)

except ObjectNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Available objects: {e.details.get('available')}")

except RateLimitError as e:
    retry_after = e.details.get('retry_after')
    print(f"Rate limited! Wait {retry_after} seconds")

except ValidationError as e:
    print(f"Invalid data: {e.message}")

finally:
    client.close()
```

### Low-Level API Access

```python
# Direct endpoint calls for advanced use cases
result = client.call_endpoint(
    endpoint="/v1/products",
    method="GET",
    params={"limit": 10, "type": "service"}
)
```

## Authentication

### Environment Variables (Recommended)

Set these environment variables before running:

```bash
# Required
export STRIPE_API_KEY="sk_test_..."

# Optional
export STRIPE_BASE_URL="https://api.stripe.com"
```

Then initialize:

```python
client = StripeDriver.from_env()
```

### Direct Credentials

```python
client = StripeDriver(
    api_key="sk_test_...",
    base_url="https://api.stripe.com"
)
```

### Getting Your API Key

1. Log in to [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **API keys**
3. Copy your **Secret key** (starts with `sk_`)
4. Set `STRIPE_API_KEY` environment variable

## API Reference

### Supported Resources

The driver supports 30+ Stripe resource types:

- `account` - Connected account management
- `account_session` - Temporary access sessions
- `charge` - Payment charges
- `checkout_session` - Checkout sessions
- `credit_note` - Invoice adjustments
- `customer` - Customer management
- `customer_balance_transaction` - Customer balance operations
- `invoice` - Invoice management
- `invoice_payment` - Invoice payment tracking
- `meter_event` - Usage-based billing events
- `payment_intent` - Payment management
- `plan` - Subscription plans (legacy)
- `price` - Pricing tiers
- `product` - Product definitions
- `quote` - Pricing proposals
- `setup_attempt` - Payment method setup attempts
- `subscription_item` - Subscription items
- And 13 more...

### Core Methods

#### `read(query, limit=None, offset=None) -> List[Dict]`

Read/list resources from Stripe.

```python
# List all products with limit
products = client.read("products", limit=50)

# List customers
customers = client.read("customers", limit=10)

# List invoices
invoices = client.read("invoices", limit=25)
```

**Parameters:**
- `query` (str): Resource type path (e.g., "products", "customers", "invoices")
- `limit` (int, optional): Max records to return (1-100, default: 10)
- `offset` (str, optional): Cursor for pagination (cursor-based)

**Returns:** List of resource dictionaries

**Raises:**
- `ValidationError` - If limit exceeds 100
- `ObjectNotFoundError` - If resource type doesn't exist
- `RateLimitError` - If rate limited after retries
- `ConnectionError` - If API connection fails

#### `create(object_name, data) -> Dict`

Create a new Stripe resource.

```python
product = client.create("products", {
    "name": "My Product",
    "type": "service"
})

customer = client.create("customers", {
    "email": "customer@example.com",
    "name": "John Doe"
})

invoice = client.create("invoices", {
    "customer": "cus_123",
    "currency": "usd"
})
```

**Parameters:**
- `object_name` (str): Resource type (e.g., "products", "customers")
- `data` (dict): Resource data

**Returns:** Created resource with ID

**Raises:**
- `ValidationError` - If data is invalid
- `AuthenticationError` - If credentials invalid
- `RateLimitError` - If rate limited
- `ConnectionError` - If API connection fails

#### `update(object_name, record_id, data) -> Dict`

Update an existing Stripe resource.

```python
updated = client.update("products", "prod_123", {
    "name": "Updated Name",
    "description": "New description"
})
```

**Parameters:**
- `object_name` (str): Resource type
- `record_id` (str): Resource ID
- `data` (dict): Updated data

**Returns:** Updated resource

**Raises:**
- `ObjectNotFoundError` - If resource doesn't exist
- `ValidationError` - If data is invalid
- `RateLimitError` - If rate limited

#### `delete(object_name, record_id) -> bool`

Delete a Stripe resource.

```python
success = client.delete("products", "prod_123")
```

**Parameters:**
- `object_name` (str): Resource type
- `record_id` (str): Resource ID

**Returns:** True if successful

**Raises:**
- `ObjectNotFoundError` - If resource doesn't exist
- `RateLimitError` - If rate limited

#### `read_batched(query, batch_size=100) -> Iterator`

Read resources in batches (memory-efficient for large datasets).

```python
for batch in client.read_batched("products", batch_size=100):
    print(f"Processing {len(batch)} products")
    for product in batch:
        print(f"  - {product['name']}")
```

**Parameters:**
- `query` (str): Resource type
- `batch_size` (int): Records per batch (max 100)

**Yields:** Batches of records

#### `get_fields(object_name) -> Dict`

Get field schema for a resource type.

```python
fields = client.get_fields("product")
print(f"Product fields: {fields.keys()}")
```

**Parameters:**
- `object_name` (str): Resource type

**Returns:** Field definitions and metadata

**Raises:**
- `ObjectNotFoundError` - If resource type not supported

#### `list_objects() -> List[str]`

Get list of supported resource types.

```python
objects = client.list_objects()
if "customer" in objects:
    print("Can query customers")
```

**Returns:** List of resource type names

#### `get_capabilities() -> DriverCapabilities`

Get driver capabilities.

```python
caps = client.get_capabilities()
if caps.write:
    print("Can create records")
if caps.delete:
    print("Can delete records")
```

**Returns:** DriverCapabilities object with capability flags

#### `call_endpoint(endpoint, method, params, data) -> Dict`

Low-level API endpoint access.

```python
result = client.call_endpoint(
    endpoint="/v1/products",
    method="GET",
    params={"limit": 10}
)
```

**Parameters:**
- `endpoint` (str): API endpoint path
- `method` (str): HTTP method (GET, POST, DELETE)
- `params` (dict, optional): Query parameters
- `data` (dict, optional): Request body

**Returns:** Response data

## Pagination

Stripe uses **cursor-based pagination**. The driver handles pagination automatically:

```python
# Automatic pagination with batches
for batch in client.read_batched("products", batch_size=100):
    process_batch(batch)

# Manual pagination
products = client.read("products", limit=100)
```

**Pagination Limits:**
- Maximum page size: 100 records
- Default page size: 10 records
- Pagination style: Cursor-based (using `starting_after` parameter)

## Capabilities

The driver supports:

- ✅ **Read Operations** - Query Stripe resources
- ✅ **Create Operations** - Create new resources
- ✅ **Update Operations** - Modify existing resources
- ✅ **Delete Operations** - Remove resources
- ✅ **Batch Reading** - Cursor-based pagination
- ✅ **Relationships** - Expand related resources
- ❌ **Bulk Operations** - Not supported by Stripe API
- ❌ **Query Language** - REST API only, no query language
- ❌ **Transactions** - Not supported

## Rate Limiting

Stripe enforces rate limits. The driver automatically handles rate limiting:

```python
from stripe_driver import RateLimitError

try:
    products = client.read("products")
except RateLimitError as e:
    retry_after = e.details['retry_after']
    print(f"Rate limited. Wait {retry_after} seconds")
    time.sleep(retry_after)
    # Retry operation
```

**Rate Limiting Features:**
- Automatic exponential backoff retry
- Configurable max retries (default: 3)
- Respects `Retry-After` header from API
- Structured error messages with retry timing

**Configure Retries:**

```python
client = StripeDriver.from_env(
    max_retries=5,  # More aggressive retry
    timeout=60      # Longer timeout
)
```

## Error Handling

The driver provides structured exceptions:

```python
from stripe_driver import (
    AuthenticationError,
    ConnectionError,
    ObjectNotFoundError,
    ValidationError,
    RateLimitError,
    TimeoutError
)

try:
    product = client.create("products", {"name": "Test"})

except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    print(f"Details: {e.details}")

except ValidationError as e:
    print(f"Invalid data: {e.message}")
    param = e.details.get('param')
    print(f"Problem field: {param}")

except RateLimitError as e:
    print(f"Rate limited: {e.message}")
    retry_after = e.details.get('retry_after')
    print(f"Retry after {retry_after} seconds")

except ConnectionError as e:
    print(f"Connection failed: {e.message}")
    print(f"Suggestion: {e.details.get('suggestion')}")

except TimeoutError as e:
    print(f"Timed out after {e.details['timeout']}s")
```

### Error Types

| Exception | Status | Description |
|-----------|--------|-------------|
| `AuthenticationError` | 401/403 | Invalid credentials or permissions |
| `ValidationError` | 400 | Invalid request parameters |
| `ObjectNotFoundError` | 404 | Resource doesn't exist |
| `RateLimitError` | 429 | Too many requests |
| `ConnectionError` | 5xx | API server error or network issue |
| `TimeoutError` | - | Request timed out |

## Common Patterns

### List All Customers

```python
customers = client.read("customers", limit=100)
for customer in customers:
    print(f"{customer['email']}: {customer.get('name', 'N/A')}")
```

### Batch Process Products

```python
total = 0
for batch in client.read_batched("products", batch_size=50):
    process_batch(batch)
    total += len(batch)
print(f"Processed {total} total products")
```

### Create Multiple Resources

```python
for item in items_to_create:
    product = client.create("products", {
        "name": item['name'],
        "type": "service"
    })
    print(f"Created: {product['id']}")
```

### Update with Error Handling

```python
try:
    updated = client.update("products", product_id, {
        "name": new_name
    })
    print(f"Updated successfully")
except ObjectNotFoundError:
    print(f"Product {product_id} not found")
```

### Search and Update

```python
products = client.read("products", limit=10)
for product in products:
    if "old" in product['name'].lower():
        client.update("products", product['id'], {
            "name": product['name'].replace("old", "new")
        })
```

## Troubleshooting

### Authentication Issues

```
AuthenticationError: Authentication failed: Invalid API key
```

**Solution:**
- Verify `STRIPE_API_KEY` is set correctly
- Ensure key starts with `sk_` (not `pk_` or `rk_`)
- Check key is not revoked in Stripe Dashboard

### Rate Limiting

```
RateLimitError: Rate limit exceeded
```

**Solution:**
- Reduce request volume
- Increase `max_retries` parameter
- Use `read_batched()` for large datasets
- Add delays between requests

### Connection Errors

```
ConnectionError: Cannot reach Stripe API
```

**Solution:**
- Check internet connection
- Verify `STRIPE_BASE_URL` is correct
- Ensure Stripe API is not down (check status.stripe.com)

### Timeout Errors

```
TimeoutError: Request timed out after 30s
```

**Solution:**
- Increase `timeout` parameter
- Reduce `limit` for large queries
- Use `read_batched()` for memory-intensive operations

## Configuration

### Environment Variables

```bash
# Required
STRIPE_API_KEY=sk_test_...

# Optional
STRIPE_BASE_URL=https://api.stripe.com
```

### Constructor Parameters

```python
client = StripeDriver(
    api_key="sk_test_...",           # API key
    base_url="https://api.stripe.com", # Base URL
    timeout=30,                       # Request timeout
    max_retries=3,                    # Rate limit retries
    debug=False                       # Debug logging
)
```

## Development

### Running Tests

```bash
pip install pytest pytest-mock
pytest tests/
```

### Debug Mode

```python
client = StripeDriver.from_env(debug=True)

# Enables detailed logging
# [DEBUG] GET https://api.stripe.com/v1/products params=...
# [DEBUG] Connection validation successful
```

## API Documentation

- [Stripe API Docs](https://docs.stripe.com/api) - Complete API reference
- [Stripe Products Guide](https://docs.stripe.com/products) - Product setup
- [Stripe Payments](https://docs.stripe.com/payments) - Payment integration
- [Stripe Billing](https://docs.stripe.com/billing) - Subscription billing

## Limitations

- **No Bulk Operations** - Stripe API doesn't support batch create/update/delete
- **No Query Language** - REST API only, no SOQL/SQL queries
- **Pagination Limits** - Maximum 100 records per request
- **No Transactions** - Not supported by Stripe API

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: GitHub Issues
- **Documentation**: [Stripe API Docs](https://docs.stripe.com/api)
- **Status**: [Stripe Status Page](https://status.stripe.com)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-19
**API Version**: v1, v2
