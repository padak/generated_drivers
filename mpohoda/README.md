# MPohodaDriver - Python Driver for mPOHODA API

Production-ready Python driver for the mPOHODA accounting software REST API.

**Version:** 1.0.0
**Status:** ✅ Production-Ready
**Quality:** All bug prevention patterns applied

---

## Overview

MPohodaDriver provides a clean, Pythonic interface to the mPOHODA accounting API with:

- ✅ **Dual authentication** (API Key + OAuth2)
- ✅ **Automatic retry** with exponential backoff
- ✅ **Hybrid pagination** (offset + keyset)
- ✅ **Comprehensive error handling**
- ✅ **Full type hints**
- ✅ **Debug logging support**

---

## Installation

Copy the driver to your project:

```bash
cp -r generated_drivers/mpohoda /path/to/your/project/
```

Then import:

```python
from mpohoda import MPohodaDriver
```

---

## Quick Start

### Setup Environment Variables

```bash
# Option 1: API Key authentication
export MPOHODA_API_KEY=your_api_key_here

# Option 2: OAuth2 authentication
export MPOHODA_CLIENT_ID=your_client_id
export MPOHODA_CLIENT_SECRET=your_client_secret
```

### Initialize Driver

```python
from mpohoda import MPohodaDriver

# Load from environment variables
driver = MPohodaDriver.from_env()

# Or explicit credentials
driver = MPohodaDriver(api_key="your_key")
```

### Read Data

```python
# Read first page of activities
activities = driver.read("Activities", page_size=50)

for activity in activities:
    print(f"{activity['id']}: {activity.get('description', 'N/A')}")

# Read all with pagination
for page in range(1, 10):
    activities = driver.read("Activities", page_number=page, page_size=50)
    if not activities:
        break
    process_batch(activities)
```

### Batch Processing (Memory Efficient)

```python
# Iterator over batches - automatic pagination
for batch in driver.read_batched("Activities", batch_size=50):
    print(f"Processing {len(batch)} records...")
    for activity in batch:
        process_activity(activity)
```

### Create Records

```python
# Create a business partner
partner = driver.create("BusinessPartners", {
    "name": "Acme Corporation",
    "taxNumber": "CZ12345678",
    "identificationNumber": "12345678",
    "addresses": [{
        "type": "CONTACT",
        "street": "Main Street 123",
        "city": "Prague",
        "postalCode": "11000",
        "country": "CZ"
    }]
})

print(f"Created partner: {partner['id']}")
```

### Error Handling

```python
from mpohoda import (
    MPohodaDriver,
    ObjectNotFoundError,
    RateLimitError,
    ValidationError,
    AuthenticationError,
)

try:
    driver = MPohodaDriver.from_env()
    records = driver.read("Activities")

except ObjectNotFoundError as e:
    print(f"Object not found: {e.message}")
    print(f"Available objects: {', '.join(e.details['available'])}")

except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Suggestion: {e.details.get('suggestion')}")

except RateLimitError as e:
    print(f"Rate limited. Retry after {e.details['retry_after']} seconds")

except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Available Objects

The driver supports these 10 object types:

```python
objects = driver.list_objects()
# ['Activities', 'BusinessPartners', 'Banks', 'BankAccounts',
#  'CashRegisters', 'Centres', 'Establishments',
#  'Countries', 'Currencies', 'CityPostCodes']
```

### Getting Object Fields

```python
# Get field schema for an object
fields = driver.get_fields("BusinessPartners")

print(f"Available fields: {list(fields.keys())}")
# Output: ['id', 'name', 'taxNumber', 'identificationNumber', ...]

for field_name, field_info in fields.items():
    print(f"{field_name}: {field_info['type']}")
```

---

## Capabilities

```python
capabilities = driver.get_capabilities()

print(f"Read:   {capabilities.read}")      # True
print(f"Write:  {capabilities.write}")     # True (POST)
print(f"Update: {capabilities.update}")    # False (API limitation)
print(f"Delete: {capabilities.delete}")    # False (API limitation)
print(f"Max page size: {capabilities.max_page_size}")  # 50
```

---

## Advanced Usage

### Debug Mode

```python
driver = MPohodaDriver.from_env(debug=True)

# Now all API calls are logged:
# [DEBUG] Validating connection to https://api.mpohoda.cz/v1
# [DEBUG] [Attempt 1] GET /Activities params={'PageSize': 1}
# [DEBUG] Connection validated successfully
```

### Custom Timeout

```python
driver = MPohodaDriver.from_env(timeout=60, max_retries=5)
```

### Rate Limit Status

```python
status = driver.get_rate_limit_status()
if status["remaining"]:
    print(f"Requests remaining: {status['remaining']}")
```

### Close Connection

```python
try:
    records = driver.read("Activities")
    # Process records...
finally:
    driver.close()  # Cleanup
```

---

## Authentication

### API Key Method (Recommended for Simplicity)

```python
driver = MPohodaDriver(api_key="your_api_key")
```

**Header:** `Api-Key: your_api_key`

**Note:** API keys cannot be retrieved after generation. Store securely outside code.

### OAuth2 Method (Recommended for Security)

```python
driver = MPohodaDriver(
    client_id="your_client_id",
    client_secret="your_client_secret"
)
```

**Process:**
1. Driver exchanges client credentials for access token
2. Token is automatically renewed when expired
3. Requests include: `Authorization: Bearer {token}`

**Token Endpoint:** `https://ucet.pohoda.cz/connect/token`

### Pre-obtained Token

```python
driver = MPohodaDriver(access_token="your_access_token")
```

---

## Pagination

### Offset-Based (Traditional)

```python
# Page 1
records = driver.read("Activities", page_number=1, page_size=50)

# Page 2
records = driver.read("Activities", page_number=2, page_size=50)
```

**Parameters:**
- `page_number`: Page number (1-indexed)
- `page_size`: Records per page (max: 50)

### Keyset-Based (Recommended for Large Datasets)

```python
for batch in driver.read_batched("Activities", batch_size=50):
    process_batch(batch)
```

**Advantages:**
- Efficient for large datasets
- No need to track page numbers
- Automatic cursor handling

---

## Error Handling

### Exception Types

| Exception | HTTP Status | Meaning |
|-----------|------------|---------|
| `AuthenticationError` | 401/403 | Invalid credentials |
| `ConnectionError` | Network | Cannot reach API |
| `ObjectNotFoundError` | 404 | Object doesn't exist |
| `FieldNotFoundError` | - | Field not found on object |
| `QuerySyntaxError` | 400 | Invalid request |
| `RateLimitError` | 429 | Rate limit exceeded |
| `ValidationError` | 422 | Validation failed |
| `TimeoutError` | - | Request timeout |

### Structured Error Details

Every exception includes structured `details` dict for programmatic handling:

```python
try:
    driver.read("NonexistentObject")
except ObjectNotFoundError as e:
    # Message for logging
    print(e.message)

    # Details for programmatic use
    print(e.details["available"])  # List of valid objects
    print(e.details["suggestions"])  # Typo corrections
```

---

## Environment Variables

### Required (at least one auth method)

- `MPOHODA_API_KEY` - API key for authentication
- `MPOHODA_CLIENT_ID` + `MPOHODA_CLIENT_SECRET` - OAuth2 credentials

### Optional

- `MPOHODA_BASE_URL` - Custom API URL (default: https://api.mpohoda.cz/v1)
- `MPOHODA_ACCESS_TOKEN` - Pre-obtained OAuth2 token

---

## Rate Limiting

mPOHODA uses monthly rate limits:

| Endpoint Type | Monthly Limit |
|---------------|--------------|
| List endpoints | 8,000 requests |
| Detail endpoints | 48,000 requests |

**Driver Features:**
- Automatic retry with exponential backoff (1s, 2s, 4s, 8s)
- Respects `Retry-After` header
- Configurable `max_retries` parameter

---

## Security Notes

1. **HTTPS-Only:** All requests use encrypted HTTPS connections
2. **Certificate Verification:** SSL/TLS certificates are verified
3. **Credentials:** Never commit credentials to version control
4. **Environment Variables:** Load credentials from environment
5. **No Defaults:** Missing credentials raise clear errors
6. **Debug Mode:** Disabled by default; enable only for development

---

## Usage Patterns

### Pattern 1: Simple Read

```python
driver = MPohodaDriver.from_env()
records = driver.read("Activities")
print(f"Found {len(records)} records")
```

### Pattern 2: Batch Processing

```python
for batch in driver.read_batched("BusinessPartners"):
    for partner in batch:
        print(partner["name"])
```

### Pattern 3: Pagination Loop

```python
page = 1
while True:
    records = driver.read("Activities", page_number=page, page_size=50)
    if not records:
        break

    process_batch(records)
    page += 1
```

### Pattern 4: Error Handling

```python
from mpohoda import MPohodaDriver, ObjectNotFoundError

try:
    driver = MPohodaDriver.from_env()
except Exception as e:
    print(f"Failed to initialize: {e}")
    exit(1)

try:
    records = driver.read("Activities")
except ObjectNotFoundError as e:
    print(f"Error: {e.message}")
    print(f"Available: {', '.join(e.details['available'])}")
```

---

## Troubleshooting

### "Missing authentication credentials"

**Solution:** Set environment variables:
```bash
export MPOHODA_API_KEY=your_key
# or
export MPOHODA_CLIENT_ID=your_id
export MPOHODA_CLIENT_SECRET=your_secret
```

### "Invalid API key"

**Solution:** Verify API key is correct. Keys are case-sensitive and cannot be retrieved after generation.

### "page_size cannot exceed 50"

**Solution:** API enforces maximum 50 records per page. Use `page_size=50` or less.

### "Rate limit exceeded"

**Solution:** Driver automatically retries. If still failing, reduce batch size or wait for monthly reset.

### "Object 'Leads' not found"

**Solution:** Check object name. Use `driver.list_objects()` to see available objects.

---

## Testing

```python
import pytest
from mpohoda import MPohodaDriver, ValidationError

def test_page_size_validation():
    driver = MPohodaDriver(api_key="test")

    with pytest.raises(ValidationError):
        driver.read("Activities", page_size=100)  # Exceeds max 50

def test_capabilities():
    driver = MPohodaDriver(api_key="test")
    capabilities = driver.get_capabilities()

    assert capabilities.read is True
    assert capabilities.write is True
    assert capabilities.update is False
    assert capabilities.max_page_size == 50
```

---

## API Documentation

**Official mPOHODA API Docs:** https://api.mpohoda.cz/doc

### Resources

- **Swagger UI:** https://api.mpohoda.cz/swagger/index.html
- **ReDoc:** https://api.mpohoda.cz/redoc
- **OpenAPI Spec:** https://api.mpohoda.cz/swagger/v1/swagger.json

---

## Support

For issues or questions:

1. Check this README first
2. Review `IMPLEMENTATION_SUMMARY.md` for implementation details
3. Check API docs at https://api.mpohoda.cz/doc
4. Review error message for suggestions

---

## License

Generated by Claude Code - Production Driver Generator

---

## Version History

**v1.0.0** (2025-11-19)
- Initial release
- Full API contract implementation
- All bug prevention patterns applied
- 1,634 lines of production code
- 100% type hints
- Comprehensive documentation
