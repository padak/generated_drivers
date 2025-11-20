# Contributing to Fidoo8Driver

Thank you for your interest in contributing to Fidoo8Driver! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Follow Python best practices
- Test your changes thoroughly
- Document your code

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fidoo8-driver.git
cd fidoo8-driver
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Install Pre-commit Hooks (Optional)

```bash
pip install pre-commit
pre-commit install
```

## Making Changes

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow PEP 8 style guide
- Add type hints to new code
- Write docstrings for all public methods
- Add comments for complex logic

### 3. Format Code

```bash
black .
isort .
```

### 4. Run Linting

```bash
flake8 fidoo8
mypy fidoo8
```

### 5. Run Tests

```bash
pytest
pytest --cov=fidoo8  # With coverage
```

## Code Style

### Imports

```python
# Group imports: standard library, third-party, local
import os
import sys
from typing import Dict, List, Optional

import requests

from fidoo8 import Fidoo8Driver
```

### Type Hints

```python
def read(
    self,
    query: str,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """Get data from API."""
    pass
```

### Docstrings

```python
def method(self, param1: str, param2: int = 10) -> bool:
    """
    Brief description of what method does.

    Longer description explaining the behavior,
    parameters, and usage.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Description of return value

    Raises:
        ValueError: When something is invalid
        ConnectionError: When API unreachable

    Example:
        >>> result = obj.method("test")
        >>> print(result)
        True
    """
    pass
```

## Adding Features

### 1. Update Core Code

- Add method to `client.py`
- Update `base.py` if adding abstract method
- Add exception type if needed to `exceptions.py`

### 2. Add Docstring

```python
def new_feature(self) -> str:
    """Brief description."""
    pass
```

### 3. Add Example

Create `examples/new_feature.py` demonstrating usage

### 4. Update Documentation

Update `README.md` or `examples/README.md` if relevant

### 5. Add Tests (Optional)

Create `tests/test_new_feature.py`

## Reporting Issues

### Bug Reports

Include:
- Python version
- Fidoo8Driver version
- Error message and traceback
- Minimal code to reproduce
- Expected vs actual behavior

### Feature Requests

Include:
- Use case and motivation
- Proposed API/interface
- Any constraints or considerations

## Pull Request Process

### 1. Create Pull Request

```bash
git push -u origin feature/your-feature-name
gh pr create --title "Brief description" --body "Detailed description"
```

### 2. PR Description

```markdown
## Summary
Brief description of changes

## Motivation
Why this change is needed

## Changes
- Change 1
- Change 2

## Testing
How to test this feature

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes
```

### 3. Address Feedback

- Respond to comments promptly
- Make requested changes
- Push updates to same branch
- Request re-review

### 4. Merge

Once approved, maintainer will merge.

## Testing Guidelines

### Unit Tests

```python
def test_read_users():
    """Test reading users from API."""
    client = Fidoo8Driver(api_key="test_key", ...)
    result = client.read("User", limit=10)
    assert len(result) == 10
```

### Integration Tests

```python
def test_end_to_end():
    """Test complete workflow."""
    client = Fidoo8Driver.from_env()
    try:
        users = client.read("User", limit=5)
        assert len(users) > 0
    finally:
        client.close()
```

### Run Tests

```bash
pytest                           # Run all tests
pytest -v                       # Verbose
pytest --cov=fidoo8             # With coverage
pytest -k test_name             # Specific test
pytest fidoo8/tests/            # Specific directory
```

## Documentation

### Update README.md

For major features, update the appropriate section:
- Installation
- Quick Start
- Usage Patterns
- API Reference
- Troubleshooting

### Update Examples

Create new example file demonstrating feature

### Update Docstrings

All public methods must have docstrings with examples

## Changelog

Update `CHANGELOG.md` (if exists) with:
- Version number
- Date
- Changes made
- Breaking changes

Format:

```markdown
## [1.0.0] - 2025-11-19

### Added
- New feature X

### Changed
- Updated behavior of Y

### Fixed
- Fixed bug in Z

### Breaking Changes
- Changed API of method A
```

## Release Process

Maintainers handle releases:

```bash
# Update version in __init__.py
# Update CHANGELOG.md
# Create git tag
git tag -a v1.0.0 -m "Release version 1.0.0"
# Build and publish
python -m build
twine upload dist/*
```

## Questions?

- Check existing issues/PRs
- Review documentation
- Open discussion issue
- Email: support@fidoo.com

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for contributing to Fidoo8Driver! 🚀
