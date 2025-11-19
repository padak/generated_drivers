# Installation Guide

Complete guide to installing and configuring the mPOHODA Python Driver.

---

## Quick Start (5 minutes)

### 1. Install the driver

```bash
# From PyPI (recommended)
pip install mpohoda-driver

# Or from source
git clone https://github.com/anthropics/agent-driver.git
cd agent-driver/generated_drivers/mpohoda
pip install -e .
```

### 2. Setup credentials

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your credentials
# Option A: API Key
MPOHODA_API_KEY=your_api_key

# Option B: OAuth2
MPOHODA_CLIENT_ID=your_client_id
MPOHODA_CLIENT_SECRET=your_client_secret
```

### 3. Test installation

```python
from mpohoda import MPohodaDriver

# Initialize from environment
driver = MPohodaDriver.from_env()

# Read data
activities = driver.read("Activities")
print(f"Found {len(activities)} activities")

# Cleanup
driver.close()
```

---

## Detailed Installation

### Option A: Production Install (PyPI)

```bash
# Install from PyPI
pip install mpohoda-driver

# Verify installation
python -c "from mpohoda import MPohodaDriver; print(MPohodaDriver.__doc__)"
```

**Pros:**
- ✅ Simple one-command install
- ✅ Automatic dependency resolution
- ✅ Easy to update: `pip install --upgrade mpohoda-driver`

**Cons:**
- ❌ Can only use released versions
- ❌ Cannot modify source code

### Option B: Development Install (From Source)

```bash
# Clone the repository
git clone https://github.com/anthropics/agent-driver.git
cd agent-driver/generated_drivers/mpohoda

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

**Pros:**
- ✅ Can modify source code
- ✅ Access to latest development version
- ✅ Can contribute changes

**Cons:**
- ❌ More setup required
- ❌ Need git installed

### Option C: Manual Install

```bash
# Clone or download the driver
git clone https://github.com/anthropics/agent-driver.git
cd agent-driver/generated_drivers/mpohoda

# Install dependencies
pip install -r requirements.txt

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Virtual Environment Setup

### Using venv (built-in)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install driver
pip install mpohoda-driver

# Deactivate when done
deactivate
```

### Using virtualenv

```bash
# Install virtualenv
pip install virtualenv

# Create environment
virtualenv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install driver
pip install mpohoda-driver
```

### Using Conda

```bash
# Create environment
conda create -n mpohoda-env python=3.9

# Activate
conda activate mpohoda-env

# Install driver
pip install mpohoda-driver
```

---

## Configuration

### Environment Variables

Create `.env` file with credentials:

```bash
# Copy template
cp .env.example .env

# Edit .env
nano .env
```

**Required (at least one auth method):**
```bash
MPOHODA_API_KEY=your_key
# OR
MPOHODA_CLIENT_ID=your_id
MPOHODA_CLIENT_SECRET=your_secret
```

**Optional:**
```bash
MPOHODA_BASE_URL=https://api.mpohoda.cz/v1
MPOHODA_ACCESS_TOKEN=your_token
```

### Using python-dotenv

```bash
# Install python-dotenv
pip install python-dotenv

# Load .env in code
from dotenv import load_dotenv
load_dotenv()

from mpohoda import MPohodaDriver
driver = MPohodaDriver.from_env()
```

### Docker Setup

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install mpohoda-driver

# Copy application code
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

CMD ["python", "your_script.py"]
```

**Build and run:**
```bash
# Build image
docker build -t mpohoda-app .

# Run container with environment file
docker run --env-file .env mpohoda-app
```

### Docker Compose Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mpohoda-app:
    build: .
    env_file: .env
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./data:/app/data
```

**Run:**
```bash
# Start services
docker-compose up

# Stop services
docker-compose down
```

---

## Verification

### Test Installation

```python
#!/usr/bin/env python
"""Verify mPOHODA driver installation"""

from mpohoda import MPohodaDriver

print("✓ Import successful")

driver = MPohodaDriver.from_env()
print("✓ Driver initialized")

capabilities = driver.get_capabilities()
print(f"✓ Capabilities: Read={capabilities.read}, Write={capabilities.write}")

objects = driver.list_objects()
print(f"✓ Found {len(objects)} objects: {', '.join(objects[:3])}...")

driver.close()
print("✓ All checks passed!")
```

**Run:**
```bash
python verify_install.py
```

### Check Version

```python
import mpohoda
print(f"mPOHODA Driver v{mpohoda.__version__}")
```

---

## Troubleshooting

### "No module named 'mpohoda'"

**Solution:**
```bash
# Verify installation
pip show mpohoda-driver

# If not installed:
pip install mpohoda-driver

# If editable install has issues:
pip install -e .
```

### "Missing authentication credentials"

**Solution:**
```bash
# Create .env file
cp .env.example .env

# Add your credentials
nano .env

# Verify loading
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('MPOHODA_API_KEY'))"
```

### "ImportError: cannot import name 'MPohodaDriver'"

**Solution:**
```bash
# Verify package structure
python -c "import mpohoda; print(mpohoda.__file__)"

# Reinstall if needed
pip uninstall mpohoda-driver
pip install mpohoda-driver
```

### Dependency conflicts

**Solution:**
```bash
# Check versions
pip list | grep -E "requests|urllib3"

# Update dependencies
pip install --upgrade requests urllib3

# Or use requirements file
pip install -r requirements.txt
```

---

## Development Setup

### Install Development Dependencies

```bash
# Install with dev tools
pip install -r requirements-dev.txt
pip install -e .
```

### Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mpohoda

# Run specific test
pytest tests/test_auth.py
```

### Code Quality

```bash
# Format code
black mpohoda/

# Sort imports
isort mpohoda/

# Lint
pylint mpohoda/

# Type check
mypy mpohoda/
```

---

## System Requirements

- **Python:** 3.7 or higher
- **OS:** Linux, macOS, Windows
- **Network:** HTTPS connection to https://api.mpohoda.cz
- **Disk:** ~50 MB (with dependencies)
- **Memory:** Minimal (~10 MB runtime)

### Python Version Support

| Python | Status | Notes |
|--------|--------|-------|
| 3.7 | ✅ Supported | Tested and verified |
| 3.8 | ✅ Supported | Tested and verified |
| 3.9 | ✅ Supported | Tested and verified |
| 3.10 | ✅ Supported | Tested and verified |
| 3.11 | ✅ Supported | Tested and verified |
| 3.12 | ✅ Supported | Tested and verified |

---

## Getting Credentials

### API Key Method

1. Go to https://app.mpohoda.cz/otevrene-api
2. Create new API key
3. Copy key to `.env`

```bash
MPOHODA_API_KEY=your_key_here
```

### OAuth2 Method (Recommended)

1. Go to https://app.mpohoda.cz/otevrene-api
2. Create new OAuth2 application
3. Copy Client ID and Client Secret to `.env`

```bash
MPOHODA_CLIENT_ID=your_id_here
MPOHODA_CLIENT_SECRET=your_secret_here
```

---

## Next Steps

After installation:

1. **Read the README:** `cat README.md`
2. **Run examples:** `python examples/basic_usage.py`
3. **Read the guide:** See `examples/README.md`
4. **Check API docs:** https://api.mpohoda.cz/doc

---

## Support

**Documentation:**
- README.md - User guide
- examples/ - Example scripts
- https://api.mpohoda.cz/doc - Official API docs

**Issues:**
- Check existing issues on GitHub
- Report bugs with reproduction steps
- Include Python version and environment info

---

**Installation Date:** 2025-11-19
**Last Updated:** 2025-11-19
