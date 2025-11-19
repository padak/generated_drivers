# Odoo Driver

A production-grade Python driver for the Odoo External RPC API (JSON-RPC 2.0).

## Overview

This driver provides a Pythonic interface to Odoo's External RPC API, enabling programmatic access to all Odoo models and operations. It handles authentication, error management, pagination, and connection pooling automatically.

**Odoo Version:** 19.0+
**Python Version:** 3.8+

## Installation

```bash
pip install requests
```

## Quick Start

### 1. Get Your API Key

In Odoo, go to Settings → Users → Your User → Security → New API Key

### 2. Set Environment Variables

```bash
export ODOO_BASE_URL="https://your-instance.odoo.com"
export ODOO_DATABASE="your_database_name"
export ODOO_API_KEY="your_user_api_key"
```

### 3. Connect and Query

```python
from odoo_driver import OdooDriver

# Load from environment
client = OdooDriver.from_env()

# List available models
models = client.list_objects()
print(f"Found {len(models)} models: {models[:5]}")

# Discover fields
fields = client.get_fields("res.partner")
print(f"Partner fields: {list(fields.keys())}")

# Query data using Odoo Domain Language
partners = client.read("[['active', '=', True], ['customer', '=', True]]", limit=50)
print(f"Found {len(partners)} active customers")

# Create a record
new_partner = client.create("res.partner", {
    "name": "Acme Corporation",
    "email": "info@acme.com",
    "customer": True
})
print(f"Created partner with ID: {new_partner['id']}")

# Update a record
client.update("res.partner", new_partner['id'], {
    "phone": "+1-555-0123"
})

# Delete a record (use with caution!)
client.delete("res.partner", new_partner['id'])

# Cleanup
client.close()
```

## Authentication

### Method 1: Environment Variables (Recommended)

```python
from odoo_driver import OdooDriver

client = OdooDriver.from_env()
```

Required environment variables:
- `ODOO_BASE_URL` - Odoo instance URL (e.g., https://odoo.example.com)
- `ODOO_DATABASE` - Database name (e.g., production)
- `ODOO_API_KEY` - User's API key (from Settings → Users → Security)

### Method 2: Explicit Credentials

```python
from odoo_driver import OdooDriver

client = OdooDriver(
    base_url="https://odoo.example.com",
    database="production",
    api_key="your_api_key_here",
    timeout=30,
    max_retries=3,
    debug=False
)
```

### Security Best Practices

- Never commit API keys to version control
- Use environment variables or secure vaults
- Rotate API keys periodically
- Use separate keys for different environments

## Query Language

Odoo uses a powerful **Domain Language** for filtering (not SQL).

### Syntax

```python
domain = [['field_name', 'operator', 'value']]
```

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `['status', '=', 'draft']` |
| `!=` | Not equals | `['active', '!=', False]` |
| `>` | Greater than | `['price', '>', 100]` |
| `<` | Less than | `['quantity', '<', 10]` |
| `>=` | Greater or equal | `['date', '>=', '2025-01-01']` |
| `<=` | Less or equal | `['date', '<=', '2025-12-31']` |
| `in` | In list | `['status', 'in', ['draft', 'confirmed']]` |
| `not in` | Not in list | `['status', 'not in', ['cancelled']]` |
| `like` | LIKE search | `['name', 'like', 'John%']` |
| `ilike` | Case-insensitive LIKE | `['name', 'ilike', '%john%']` |

### Logical Operators

```python
# AND (default - implicit)
[['name', '=', 'John'], ['active', '=', True]]

# OR (use '|')
['|', ['status', '=', 'draft'], ['status', '=', 'confirmed']]

# NOT (use '!')
['!', ['active', '=', True]]

# Complex: (status = 'draft' OR status = 'confirmed') AND active = True
['&', '|', ['status', '=', 'draft'], ['status', '=', 'confirmed'], ['active', '=', True]]
```

### Query Examples

```python
# Active contacts
"[['active', '=', True]]"

# Customers from France
"[['customer', '=', True], ['country_id', '=', 'France']]"

# Orders created in last 30 days
"[['create_date', '>=', '2025-10-19']]"

# Draft or confirmed orders
"['|', ['state', '=', 'draft'], ['state', '=', 'confirmed']]"

# Active products priced over $100
"[['active', '=', True], ['list_price', '>', 100]]"

# Search by name (case-insensitive)
"[['name', 'ilike', '%acme%']]"
```

## Capabilities

- ✅ **Read** - Query any model with powerful domain filtering
- ✅ **Create** - Insert new records
- ✅ **Update** - Modify existing records
- ✅ **Delete** - Remove records
- ✅ **Batch Operations** - All operations support bulk processing
- ✅ **Field Discovery** - Introspect model schemas
- ✅ **Pagination** - Offset/limit based pagination
- ✅ **Relationships** - Handle Many2One, One2Many, Many2Many
- ✅ **Error Handling** - Comprehensive, structured exceptions

## Common Patterns

### Pagination for Large Datasets

```python
# Read in batches (memory-efficient)
for batch in client.read_batched("[['active', '=', True]]", batch_size=100):
    print(f"Processing {len(batch)} records")
    # Process batch...
    for record in batch:
        print(record['name'])
```

### Field Discovery

```python
# Get all fields for a model
fields = client.get_fields("res.partner")

# Check if field exists and its type
if "email" in fields:
    print(f"Email field type: {fields['email']['type']}")

# List all required fields
required = [name for name, field in fields.items() if field['required']]
print(f"Required fields: {required}")
```

### Error Handling

```python
from odoo_driver.exceptions import (
    ObjectNotFoundError,
    ValidationError,
    RateLimitError,
    AuthenticationError
)

try:
    # Try to query non-existent model
    results = client.read("[['id', '=', 1]]")

except ObjectNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Available objects: {e.details['available'][:5]}")

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Missing fields: {e.details.get('missing_fields', [])}")

except RateLimitError as e:
    print(f"Rate limited! Retry after {e.details['retry_after']} seconds")

except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
    print(f"Required env vars: {e.details['required_env_vars']}")
```

### Batch Create

```python
# Create multiple records
records_to_create = [
    {"name": "Company A", "customer": True},
    {"name": "Company B", "supplier": True},
    {"name": "Company C", "customer": True, "supplier": True},
]

created_ids = []
for data in records_to_create:
    record = client.create("res.partner", data)
    created_ids.append(record['id'])
    print(f"Created: {record['name']} (ID: {record['id']})")
```

### Batch Update

```python
# Update multiple records
partner_ids = [1, 2, 3, 4, 5]

for pid in partner_ids:
    client.update("res.partner", pid, {
        "active": True,
        "customer": True
    })
    print(f"Updated partner {pid}")
```

## API Reference

### OdooDriver Class

#### `from_env(**kwargs) -> OdooDriver`

Create driver from environment variables.

```python
client = OdooDriver.from_env(debug=True)
```

**Environment Variables:**
- `ODOO_BASE_URL` - Instance URL
- `ODOO_DATABASE` - Database name
- `ODOO_API_KEY` - API key

#### `get_capabilities() -> DriverCapabilities`

Get driver capabilities.

```python
caps = client.get_capabilities()
print(f"Query language: {caps.query_language}")  # "Odoo Domain Language"
print(f"Max page size: {caps.max_page_size}")   # 1000
```

#### `list_objects() -> List[str]`

Discover all available models.

```python
models = client.list_objects()
# Returns: ["res.partner", "res.users", "sale.order", ...]
```

#### `get_fields(model_name: str) -> Dict[str, Dict]`

Get field schema for a model.

```python
fields = client.get_fields("res.partner")
# Returns: {"name": {"type": "char", "required": True, ...}, ...}
```

#### `read(query: str, limit: int = 80, offset: int = 0) -> List[Dict]`

Query records using domain language.

```python
partners = client.read("[['active', '=', True]]", limit=100, offset=0)
```

#### `read_batched(query: str, batch_size: int = 80) -> Iterator[List[Dict]]`

Query records in batches (memory-efficient).

```python
for batch in client.read_batched("[['active', '=', True]]"):
    process_batch(batch)
```

#### `create(model: str, data: Dict) -> Dict`

Create a new record.

```python
record = client.create("res.partner", {
    "name": "New Company",
    "email": "contact@example.com"
})
```

#### `update(model: str, record_id: str, data: Dict) -> Dict`

Update an existing record.

```python
client.update("res.partner", "42", {
    "phone": "+1-555-0123"
})
```

#### `delete(model: str, record_id: str) -> bool`

Delete a record (use with caution!).

```python
client.delete("res.partner", "42")
```

#### `close()`

Close session and cleanup.

```python
client.close()
```

## Rate Limits

Odoo does not publish explicit rate limits, but respects your instance's configuration:

- Driver automatically retries failed requests with exponential backoff
- Default retries: 3 attempts (2s, 4s, 8s)
- Default timeout: 30 seconds

Configure when creating driver:

```python
client = OdooDriver.from_env(
    timeout=60,      # Increase timeout for slow queries
    max_retries=5    # More retry attempts
)
```

## Troubleshooting

### Authentication Error: "Invalid API key"

1. Verify API key is set: `echo $ODOO_API_KEY`
2. Generate new key in Odoo: Settings → Users → Your User → Security → New API Key
3. Check database name matches: `echo $ODOO_DATABASE`
4. Verify base URL: `echo $ODOO_BASE_URL`

### Model Not Found Error

1. Check model name spelling (case-sensitive): `res.partner` not `res.Partner`
2. List available models: `client.list_objects()`
3. Verify model is installed in database

### Field Not Found Error

1. Get all fields: `client.get_fields("res.partner")`
2. Check field name spelling
3. Field might be in different model

### Timeout Errors

1. Reduce query size (fewer records)
2. Increase timeout: `OdooDriver.from_env(timeout=60)`
3. Use batched reading for large datasets
4. Check Odoo server health

### Rate Limit Errors

1. Reduce batch sizes
2. Add delays between requests
3. Check `retry_after` in error details
4. Configure more retries: `OdooDriver.from_env(max_retries=5)`

## Common Models Reference

| Model | Purpose |
|-------|---------|
| `res.partner` | Contacts/Companies |
| `res.users` | User accounts |
| `res.company` | Companies |
| `sale.order` | Sales orders |
| `purchase.order` | Purchase orders |
| `account.move` | Invoices/Journal entries |
| `stock.move` | Inventory movements |
| `project.project` | Projects |
| `project.task` | Project tasks |
| `ir.model` | Model metadata |
| `ir.model.fields` | Field metadata |

## Examples

See `examples/` directory for complete working examples:
- `list_all_partners.py` - Query all contacts
- `create_partner.py` - Create new contact
- `batch_operations.py` - Batch create/update
- `field_discovery.py` - Explore model schemas
- `error_handling.py` - Handle errors gracefully
- `pagination_large_dataset.py` - Process large result sets

## Performance Tips

1. **Use pagination** - Always specify `limit` for large queries
2. **Batch operations** - Create/update multiple records at once
3. **Connection pooling** - Driver reuses HTTP connections automatically
4. **Field selection** - Only query fields you need
5. **Index on filters** - Query on indexed fields when possible

## Security Notes

- **Never** commit API keys to version control
- **Always** use HTTPS (verify URL starts with https://)
- **Rotate** API keys periodically
- **Use** separate keys for different environments
- **Review** access permissions in Odoo for your API user

## License

MIT

## Support

For issues and questions:
1. Check this README
2. Review example scripts
3. Check Odoo documentation: https://www.odoo.com/documentation/19.0/
4. Open issue on GitHub

---

**Driver Version:** 1.0.0
**Odoo Compatibility:** 19.0+
**Python Compatibility:** 3.8+
