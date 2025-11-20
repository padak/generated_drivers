# Fidoo8Driver - Python API Driver for Fidoo

Complete Python driver for [Fidoo Expense Management API](https://www.fidoo.com/support/expense-management-en/it-specialist/specifications-api/).

## Overview

Fidoo is a comprehensive expense management platform for corporate finances. This driver provides seamless Python integration with Fidoo's complete API, enabling:

- **User Management**: Create, read, update, and delete users
- **Card Operations**: Manage personal and shared prepaid cards
- **Transaction Tracking**: Query and track all card transactions
- **Expense Management**: Create, edit, and query expenses
- **Travel Reports**: Manage travel requests and reports
- **Personal Billing**: Handle expense settlements and personal billing
- **System Settings**: Access cost centers, projects, account assignments, vehicles, and VAT configurations

## Installation

```bash
pip install fidoo8-driver
```

## Quick Start

### Using Environment Variables (Recommended)

```bash
# Set API credentials
export FIDOO_API_KEY="your_api_key_here"
export FIDOO_BASE_URL="https://api.fidoo.com/v2"  # Optional, defaults to production

# Run Python
python
```

```python
from fidoo8 import Fidoo8Driver

# Load from environment
client = Fidoo8Driver.from_env()

# Discover available objects
objects = client.list_objects()
print(f"Available objects: {objects}")

# Get field schema
fields = client.get_fields("User")
print(f"User fields: {fields.keys()}")

# Query users
users = client.read("User", limit=50)
print(f"Found {len(users)} users")

# Cleanup
client.close()
```

### Using Explicit Credentials

```python
from fidoo8 import Fidoo8Driver

client = Fidoo8Driver(
    base_url="https://api-demo.fidoo.com/v2",  # Demo environment
    api_key="your_demo_api_key"
)

# Use the client...
users = client.read("User")

client.close()
```

## Authentication

### Getting Your API Key

1. Log in to your Fidoo application
2. As Main Administrator, navigate to: **Settings → API Keys**
3. Generate a new API key
4. Copy the key and store it securely

### Environment Variables

Set these environment variables before running your code:

```bash
# Required
FIDOO_API_KEY="your_api_key_here"

# Optional (defaults shown)
FIDOO_BASE_URL="https://api.fidoo.com/v2"       # Production API
FIDOO_TIMEOUT="30"                               # Request timeout in seconds
FIDOO_MAX_RETRIES="3"                            # Retries on rate limit
FIDOO_DEBUG="false"                              # Enable debug logging
```

### Using Test Environment

```python
# Point to demo API
client = Fidoo8Driver.from_env()
# Or explicitly:
client = Fidoo8Driver(
    base_url="https://api-demo.fidoo.com/v2",
    api_key=os.getenv("FIDOO_TEST_KEY")
)
```

Request test credentials: [info@fidoo.com](mailto:info@fidoo.com)

## Available Objects

The driver supports querying these Fidoo objects:

- **User** - User profiles and permissions
- **Card** - Prepaid cards (personal and shared)
- **Transaction** - Card transactions
- **CardTransaction** - Detailed card transaction data
- **Expense** - Expense reports
- **ExpenseItem** - Individual expense line items
- **CashTransaction** - Cash wallet transactions
- **TravelReport** - Business travel reports
- **TravelRequest** - Travel requests and pre-approvals
- **TravelDetail** - Travel itinerary details
- **PersonalBilling** - Personal expense settlements
- **MVCTransaction** - Fidoo account transactions
- **CostCenter** - Cost center configurations
- **Project** - Project assignments
- **AccountAssignment** - Account pre-configurations
- **Vehicle** - Vehicle information
- **VATBreakdown** - VAT breakdowns for accounting

## Usage Patterns

### Basic Query

```python
from fidoo8 import Fidoo8Driver

client = Fidoo8Driver.from_env()

# Query a single object
users = client.read("User", limit=50)

for user in users:
    print(f"{user['firstName']} {user['lastName']} ({user['email']})")

client.close()
```

### Pagination for Large Datasets

```python
# Process large datasets efficiently with batching
client = Fidoo8Driver.from_env()

total_processed = 0

# read_batched yields batches (memory-efficient)
for batch in client.read_batched("User", batch_size=50):
    process_batch(batch)
    total_processed += len(batch)
    print(f"Processed {total_processed} users...")

client.close()

def process_batch(records):
    """Process a batch of records"""
    for record in records:
        # Your processing logic here
        pass
```

### Error Handling

```python
from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import (
    ObjectNotFoundError,
    RateLimitError,
    AuthenticationError,
)

client = Fidoo8Driver.from_env()

try:
    # Try to query an object
    results = client.read("NonExistentObject")

except ObjectNotFoundError as e:
    # Handle missing object
    print(f"Error: {e.message}")
    print(f"Available objects: {e.details['available']}")

    # Try with valid object
    results = client.read("User", limit=10)

except RateLimitError as e:
    # Handle rate limiting
    retry_after = e.details['retry_after']
    print(f"Rate limited! Retry after {retry_after} seconds")
    import time
    time.sleep(retry_after)
    results = client.read("User")

except AuthenticationError as e:
    # Handle auth failure
    print(f"Authentication failed: {e.message}")
    print("Check your FIDOO_API_KEY environment variable")

finally:
    client.close()
```

### Working with Specific Objects

#### Users

```python
client = Fidoo8Driver.from_env()

# Get all users
users = client.read("User", limit=100)

# Get specific fields
for user in users:
    print(f"User: {user.get('firstName')} {user.get('lastName')}")
    print(f"Email: {user.get('email')}")
    print(f"Status: {user.get('userState')}")
    print(f"Deactivated: {user.get('deactivated')}")
    print()

client.close()
```

#### Cards

```python
client = Fidoo8Driver.from_env()

# Get all cards
cards = client.read("Card", limit=100)

for card in cards:
    print(f"Card: {card.get('embossName')}")
    print(f"PAN: {card.get('maskedNumber')}")
    print(f"Status: {card.get('cardState')}")
    print(f"Type: {card.get('cardType')}")
    print(f"Balance: {card.get('availableBalance')} CZK")
    print()

client.close()
```

#### Expenses

```python
client = Fidoo8Driver.from_env()

# Get all expenses
expenses = client.read("Expense", limit=50)

for expense in expenses:
    print(f"Expense: {expense.get('name')}")
    print(f"Amount: {expense.get('amountCzk')} CZK")
    print(f"Currency: {expense.get('currency')}")
    print(f"State: {expense.get('state')}")
    print(f"Created: {expense.get('dateTime')}")
    print()

client.close()
```

### Creating Records

```python
client = Fidoo8Driver.from_env()

# Create a new user
new_user = client.create("User", {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+420123456789",
    "employeeNumber": "EMP001"
})

print(f"Created user: {new_user['userId']}")

client.close()
```

### Updating Records

```python
client = Fidoo8Driver.from_env()

# Update an expense
updated = client.update("Expense", "expense_id_here", {
    "name": "Updated Expense Name",
    "state": "approve"
})

print(f"Updated expense: {updated['expenseId']}")

client.close()
```

### Debug Mode

```python
import logging

# Enable debug logging to see all API calls
client = Fidoo8Driver.from_env(debug=True)

# This will log all HTTP requests and responses
users = client.read("User", limit=5)

client.close()
```

Output:
```
[DEBUG] [POST] https://api.fidoo.com/v2/user/get-users params={'limit': 5}
```

## Rate Limiting

Fidoo API implements rate limiting. The driver automatically handles this:

- **Automatic Retry**: Requests are retried with exponential backoff
- **Max Retries**: Default 3 retries (configurable)
- **Backoff**: 1s, 2s, 4s between attempts
- **After Max Retries**: `RateLimitError` is raised

### Handling Rate Limits

```python
from fidoo8 import Fidoo8Driver
from fidoo8.exceptions import RateLimitError
import time

client = Fidoo8Driver.from_env(max_retries=5)  # More aggressive retries

try:
    users = client.read("User", limit=1000)
except RateLimitError as e:
    wait_seconds = e.details['retry_after']
    print(f"Rate limited! Waiting {wait_seconds} seconds...")
    time.sleep(wait_seconds)
    # Retry manually
    users = client.read("User", limit=50)  # Smaller batch

client.close()
```

## Capabilities

Check what the driver supports:

```python
client = Fidoo8Driver.from_env()

caps = client.get_capabilities()
print(f"Read: {caps.read}")           # True
print(f"Write: {caps.write}")         # True
print(f"Update: {caps.update}")       # True
print(f"Delete: {caps.delete}")       # True
print(f"Pagination: {caps.pagination}") # PaginationStyle.CURSOR
print(f"Max page size: {caps.max_page_size}") # 100

client.close()
```

## Pagination

The driver uses **cursor-based pagination** (token-based):

```python
# Automatic pagination with read_batched
for batch in client.read_batched("User", batch_size=50):
    process(batch)  # Process 50 records at a time

# Or manual pagination with read
users = client.read("User", limit=50)  # Gets first 50
# Returns all records up to API limits
```

### Pagination Parameters

- **limit**: Records per request (1-100, default: 50)
- **offsetToken**: Token for fetching next batch (automatic)
- **nextOffsetToken**: Token in response for next batch (automatic)

## Response Field Schema

### User Fields

```
userId          string      Unique user identifier (UUID)
firstName       string      User's first name
lastName        string      User's last name
email           string      User's email address
phone           string      User's phone number
employeeNumber  string      Employee number
Position        string      User's position
userState       enum        Status: active, deleted, new
deactivated     boolean     Is user deactivated
usesApplication boolean     Has app access
kycStatus       enum        KYC status: unknown, ok, failed, refused
language        string      Application language
companyId       string      Company identifier
LastModified    datetime    Last modification timestamp
```

### Card Fields

```
cardId              string      Unique card identifier (UUID)
cardState           enum        Status: first-ordered, active, hard-blocked, soft-blocked, expired
cardType            enum        Type: personal, shared
maskedNumber        string      Masked PAN (e.g., 549546******3575)
embossName          string      Cardholder name on card
alias               string      Optional card alias
expiration          date        Card expiry date (YYYY-MM-DD)
availableBalance    number      Available balance in CZK
accountingBalance   number      Accounting balance
blockedBalance      number      Sum of uncleared transactions
userId              string      Card owner user ID
connectedUserIds    string      Connected user IDs (team card, semicolon-separated)
```

### Expense Fields

```
expenseId           string      Unique expense identifier
ownerUserId         string      Expense owner user ID
dateTime            datetime    Expense timestamp
lastEditDateTime    datetime    Last edit timestamp
name                string      Expense name
amount              number      Expense amount
amountCzk           number      Amount in CZK
currency            string      Currency code (e.g., "CZK", "EUR")
shortId             string      Short expense ID (e.g., "EX-10")
state               enum        Status: prepare, approve, approve2, accountantApprove, personalBill, export, exported
type                enum        Type: manual, card-transaction
closed              boolean     Is expense closed
```

## Troubleshooting

### Authentication Error

```
AuthenticationError: Invalid Fidoo API key
```

**Solutions:**
1. Check FIDOO_API_KEY environment variable is set
2. Verify API key is valid and not expired
3. Request new API key from Fidoo admin interface
4. Check API key has required permissions

### Object Not Found

```
ObjectNotFoundError: Object 'Leads' not found
```

**Solutions:**
1. Check spelling (case-sensitive)
2. Call `list_objects()` to see available objects
3. Use exact object name from documentation

### Rate Limit Exceeded

```
RateLimitError: API rate limit exceeded
```

**Solutions:**
1. Wait the time specified in error message
2. Reduce batch size (use smaller `limit` values)
3. Add delay between requests
4. Increase max_retries: `Fidoo8Driver(max_retries=5)`

### Connection Error

```
ConnectionError: Cannot reach Fidoo API
```

**Solutions:**
1. Check internet connection
2. Verify base_url is correct
3. Check if Fidoo API is up (https://status.fidoo.com)
4. Try demo API to test connectivity: https://api-demo.fidoo.com/v2

## API Reference

### Fidoo8Driver Methods

#### Constructor

```python
Fidoo8Driver(
    base_url: str = "https://api.fidoo.com/v2",
    api_key: str = None,
    timeout: int = 30,
    max_retries: int = 3,
    debug: bool = False
)
```

#### from_env()

```python
@classmethod
Fidoo8Driver.from_env() -> Fidoo8Driver
```

Create driver from environment variables. Raises `AuthenticationError` if required env vars missing.

#### get_capabilities()

```python
get_capabilities() -> DriverCapabilities
```

Returns driver capabilities (read, write, update, delete, pagination style, etc.).

#### list_objects()

```python
list_objects() -> List[str]
```

Get available objects (User, Card, Expense, etc.).

#### get_fields()

```python
get_fields(object_name: str) -> Dict[str, Any]
```

Get field schema for an object.

#### read()

```python
read(
    query: str,
    limit: int = 50,
    offset: int = None
) -> List[Dict[str, Any]]
```

Query an object (query is object name, not SQL).

#### read_batched()

```python
read_batched(
    query: str,
    batch_size: int = 50
) -> Iterator[List[Dict[str, Any]]]
```

Query with automatic batching (memory-efficient).

#### create()

```python
create(object_name: str, data: Dict[str, Any]) -> Dict[str, Any]
```

Create new record.

#### update()

```python
update(object_name: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]
```

Update existing record.

#### delete()

```python
delete(object_name: str, record_id: str) -> bool
```

Delete record.

#### close()

```python
close()
```

Close session and cleanup.

## DateTime Format

All timestamps use ISO 8601 format with timezone:

- `2022-09-17T13:28:35.382Z` (UTC)
- `2022-09-17T13:28:35.382+02:00` (with timezone offset)

## Currency and Numbers

- **Currency amounts**: Decimal numbers (e.g., `450.00`)
- **Currency field**: Specifies actual currency (e.g., `"CZK"`, `"EUR"`)
- **Exchange rates**: High precision decimals (e.g., `23.4244`)
- **VAT rates**: 0-1 decimal (e.g., `0.21` for 21%)

## Support

- **Documentation**: https://www.fidoo.com/support/expense-management-en/it-specialist/specifications-api/
- **API Issues**: info@fidoo.com
- **Test Environment**: Request from info@fidoo.com

## License

This driver is provided as-is for use with the Fidoo API.

## Contributing

For issues, feature requests, or improvements, please contact Fidoo support.

---

**Driver Version:** 1.0.0
**API Version:** v2
**Last Updated:** 2025-11-19
