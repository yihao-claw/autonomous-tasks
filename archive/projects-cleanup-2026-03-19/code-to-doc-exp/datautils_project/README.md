# DataUtils

A comprehensive data processing and utility library.

## Features

- **Data Validation**: Email, phone, and URL validation with country-specific support
- **Text Transformation**: Case conversion, normalization, and slugification
- **File I/O**: CSV and JSON loading/saving utilities
- **Statistical Analysis**: Mean, standard deviation, percentiles, and quartiles

## Installation

```bash
pip install datautils
```

## Quick Start

```python
from datautils import validate_email, load_csv, calculate_mean

# Validate email
is_valid, msg = validate_email("user@example.com")

# Load CSV file
data = load_csv("data.csv")

# Calculate statistics
numbers = [1, 2, 3, 4, 5]
avg = calculate_mean(numbers)
```

## Documentation

See the docstrings in each module for detailed function documentation.
