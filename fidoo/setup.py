#!/usr/bin/env python3
"""
Setup configuration for Fidoo8Driver package

Install:
    pip install -e .

For development:
    pip install -e ".[dev]"

For testing:
    pip install -e ".[test]"
"""

from setuptools import setup, find_packages
import os

# Read package info
here = os.path.abspath(os.path.dirname(__file__))

# Get version from __init__.py
version_file = os.path.join(here, "fidoo8", "__init__.py")
with open(version_file) as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

# Read README for long description
readme_file = os.path.join(here, "README.md")
with open(readme_file, encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
requirements_file = os.path.join(here, "requirements.txt")
with open(requirements_file) as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="fidoo8-driver",
    version=version,
    description="Python API Driver for Fidoo Expense Management API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Fidoo API Driver Generator",
    author_email="support@fidoo.com",
    url="https://github.com/yourusername/fidoo8-driver",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "test": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    keywords=[
        "fidoo",
        "api",
        "expense",
        "management",
        "finance",
        "integration",
        "cards",
        "transactions",
    ],
    project_urls={
        "Documentation": "https://github.com/yourusername/fidoo8-driver/blob/main/README.md",
        "Source": "https://github.com/yourusername/fidoo8-driver",
        "Bug Tracker": "https://github.com/yourusername/fidoo8-driver/issues",
        "API Reference": "https://www.fidoo.com/support/expense-management-en/it-specialist/specifications-api/",
    },
)
