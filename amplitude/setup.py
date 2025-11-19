#!/usr/bin/env python3
"""
Setup script for Amplitude Analytics Driver.

This file configures the package for distribution and installation.
Modern projects should use pyproject.toml instead, but setup.py is provided
for compatibility and direct setuptools access.

Usage:
    # Install in development mode
    pip install -e .

    # Build distribution
    python setup.py sdist bdist_wheel

    # Upload to PyPI
    python -m twine upload dist/*
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    # Package metadata
    name="amplitude-driver",
    version="1.0.0",
    author="Amplitude Driver Team",
    author_email="driver@amplitude.com",
    description="Production-ready Python driver for Amplitude Analytics APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/amplitude-driver",
    project_urls={
        "Bug Tracker": "https://github.com/your-org/amplitude-driver/issues",
        "Documentation": "https://amplitude-driver.readthedocs.io",
        "Source Code": "https://github.com/your-org/amplitude-driver",
    },
    license="MIT",

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    package_data={
        "amplitude": ["py.typed"],
    },

    # Python version requirement
    python_requires=">=3.8",

    # Dependencies
    install_requires=[
        "requests>=2.28.0,<3.0.0",
        "urllib3>=1.26.0,<2.0.0",
    ],

    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "pylint>=2.12.0",
            "mypy>=0.910",
            "isort>=5.10.0",
            "flake8>=4.0.0",
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "pytest-mock>=3.6.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
    },

    # Classifiers help users find the project
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],

    # Keywords for searching
    keywords=[
        "amplitude",
        "analytics",
        "event-tracking",
        "api",
        "driver",
        "sdk",
    ],

    # Include additional files in distribution
    include_package_data=True,
    zip_safe=False,
)
