"""
Setup configuration for mPOHODA Python Driver

Install with:
    pip install -e .          # Editable install (development)
    pip install .             # Normal install
    pip install -r requirements.txt && pip install -e .  # With dev deps

For development:
    pip install -r requirements-dev.txt
    pip install -e .
"""

from setuptools import setup, find_packages
import os

# Read version from __init__.py
version = {}
init_path = os.path.join(os.path.dirname(__file__), 'mpohoda', '__init__.py')
with open(init_path, 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
with open(readme_path, 'r', encoding='utf-8') as f:
    long_description = f.read()

# Read requirements
requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
with open(requirements_path, 'r') as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip() and not line.startswith('#')
    ]

setup(
    name='mpohoda-driver',
    version=version['__version__'],
    description='Production-ready Python driver for mPOHODA accounting software API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Claude Code',
    author_email='noreply@anthropic.com',
    url='https://github.com/anthropics/agent-driver',
    license='MIT',

    # Package discovery
    packages=find_packages(exclude=['tests', 'examples', 'docs']),

    # Requirements
    install_requires=requirements,
    python_requires='>=3.7',

    # Metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],

    # Keywords for search
    keywords=[
        'mpohoda',
        'accounting',
        'api',
        'rest',
        'client',
        'python',
        'driver',
        'czech',
    ],

    # Project URLs
    project_urls={
        'Documentation': 'https://github.com/anthropics/agent-driver/blob/main/generated_drivers/mpohoda/README.md',
        'Source': 'https://github.com/anthropics/agent-driver',
        'Tracker': 'https://github.com/anthropics/agent-driver/issues',
        'mPOHODA API': 'https://api.mpohoda.cz/doc',
    },

    # Include additional files
    include_package_data=True,

    # Entry points (optional - for CLI if added in future)
    # entry_points={
    #     'console_scripts': [
    #         'mpohoda-cli=mpohoda.cli:main',
    #     ],
    # },
)
