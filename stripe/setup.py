"""
Setup script for Stripe Driver package.

This script is provided for compatibility with older Python environments.
For modern Python (3.7+), prefer using pyproject.toml instead.

Installation:
    pip install .

Development installation:
    pip install -e ".[dev]"
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
with open(os.path.join(this_directory, "requirements.txt"), encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="stripe-driver",
    version="1.0.0",
    author="Claude Code",
    author_email="noreply@anthropic.com",
    description="Production-ready Python driver for Stripe API with automatic rate limiting, error handling, and cursor-based pagination.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anthropics/stripe-driver",
    project_urls={
        "Bug Tracker": "https://github.com/anthropics/stripe-driver/issues",
        "Documentation": "https://github.com/anthropics/stripe-driver/blob/main/README.md",
        "Repository": "https://github.com/anthropics/stripe-driver.git",
    },
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "Topic :: Internet",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.960",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=4.5.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "stripe",
        "payment",
        "api",
        "driver",
        "rest",
        "client",
        "sdk",
    ],
    license="MIT",
    zip_safe=False,
)
