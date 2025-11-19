#!/usr/bin/env python
"""
Setup script for PostHog Python Driver

This file is maintained for backward compatibility.
For new installs, use pyproject.toml instead.

Installation:
    pip install .
    or
    pip install -e .  (for development)
"""

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        # Package metadata is defined in pyproject.toml
        # This setup.py exists for compatibility with older tools
        packages=find_packages(exclude=["tests", "docs", "examples"]),
    )
