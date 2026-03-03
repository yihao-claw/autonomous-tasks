# Module `validators`


## Functions

### `validate_email(email: str) -> Tuple[(bool, str)]`

Validate if a string is a valid email address.

Args:
    email: The email string to validate
    
Returns:
    A tuple of (is_valid, error_message)
    
Examples:
    >>> validate_email("user@example.com")
    (True, "")
    >>> validate_email("invalid-email")
    (False, "Invalid email format")

**Parameters:**

- `email` (str)

**Returns:**

- Tuple[(bool, str)]


### `validate_phone(phone: str, country_code: str = 'US') -> Tuple[(bool, str)]`

Validate if a string is a valid phone number.

Supports multiple country formats:
- US: (XXX) XXX-XXXX or XXX-XXX-XXXX
- UK: +44 XXXX XXXXXX
- CN: +86 1X XXXX XXXX

Args:
    phone: The phone number string to validate
    country_code: Country code (US, UK, CN). Defaults to "US"
    
Returns:
    A tuple of (is_valid, error_message)
    
Raises:
    ValueError: If country_code is not supported

**Parameters:**

- `phone` (str)
- `country_code` (str) = 'US'

**Returns:**

- Tuple[(bool, str)]


### `validate_url(url: str, require_https: bool = False) -> Tuple[(bool, str)]`

Validate if a string is a valid URL.

Args:
    url: The URL string to validate
    require_https: If True, only accept HTTPS URLs. Defaults to False
    
Returns:
    A tuple of (is_valid, error_message)

**Parameters:**

- `url` (str)
- `require_https` (bool) = False

**Returns:**

- Tuple[(bool, str)]


### `validate_range(value: float, min_val: float, max_val: float) -> bool`

Validate if a numeric value is within a specified range.

Args:
    value: The numeric value to validate
    min_val: Minimum acceptable value (inclusive)
    max_val: Maximum acceptable value (inclusive)
    
Returns:
    True if value is within range, False otherwise

**Parameters:**

- `value` (float)
- `min_val` (float)
- `max_val` (float)

**Returns:**

- bool

