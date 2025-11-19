"""
Setup configuration for Apify Driver

This setup.py is provided for compatibility with older build systems.
For modern Python packaging, use pyproject.toml instead.

Installation:
    pip install .
    pip install -e .  (editable/development mode)
    pip install -e ".[dev]"  (with development dependencies)
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="apify-driver",
    version="1.0.0",
    author="Agent-Generated",
    author_email="noreply@anthropic.com",
    description="Production-ready Python API driver for Apify with automatic retry, pagination, and comprehensive error handling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anthropic/agent-driver",
    project_urls={
        "Bug Tracker": "https://github.com/anthropic/agent-driver/issues",
        "Documentation": "https://github.com/anthropic/agent-driver#readme",
        "Repository": "https://github.com/anthropic/agent-driver",
    },
    license="MIT",
    packages=find_packages(where=".", include=["apify_driver*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0,<3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
            "mypy>=0.910",
            "types-requests>=2.25.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords=[
        "apify",
        "api",
        "driver",
        "rest",
        "client",
        "web-scraping",
        "automation",
    ],
    zip_safe=False,
    include_package_data=True,
)
