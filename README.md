# Generated API Drivers

Python drivers for 3rd party API services with unified interface.

## Drivers

| Driver | API | Description |
|--------|-----|-------------|
| **amplitude** | Amplitude Analytics | Event tracking, user properties, export |
| **apify** | Apify Platform | Web scraping, actors, datasets |
| **fidoo** | Fidoo Expense | Expenses, cards, users |
| **mpohoda** | mPOHODA | Accounting, invoices, partners |
| **odoo** | Odoo ERP | CRM, sales, inventory (JSON-RPC) |
| **posthog** | PostHog | Product analytics, feature flags |
| **stripe** | Stripe | Payments, customers, subscriptions |

## Installation

```bash
pip install requests urllib3
```

## Usage

```python
from stripe_driver import StripeDriver

# Initialize from environment variables
client = StripeDriver.from_env()

# CRUD operations
items = client.read("customers", limit=50)
new = client.create("customers", {"email": "test@example.com"})
client.update("customers", new["id"], {"name": "Test"})
client.delete("customers", new["id"])

# Batched reading
for batch in client.read_batched("products", batch_size=100):
    process(batch)

client.close()
```

## Environment Variables

Each driver requires specific variables (API keys, URLs). See `from_env()` in respective `client.py`.

## Common Features

- `read()` / `read_batched()` - data retrieval
- `create()` / `update()` / `delete()` - write operations
- `list_objects()` - available resources
- `get_fields()` - field schemas
- Automatic retry on rate limiting
- Structured exceptions
- Context manager support

## Examples

Each driver has an `examples/` directory with usage samples.
