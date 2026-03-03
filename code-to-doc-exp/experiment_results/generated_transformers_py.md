# Module `transformers`


## Functions

### `normalize_text(text: str, lowercase: bool = True, remove_accents: bool = True) -> str`

Normalize text by removing extra whitespace and optionally converting to lowercase.

Args:
    text: Input text to normalize
    lowercase: Convert to lowercase. Defaults to True
    remove_accents: Remove accent marks. Defaults to True
    
Returns:
    Normalized text string
    
Examples:
    >>> normalize_text("  Hello   WORLD  ")
    "hello world"

**Parameters:**

- `text` (str)
- `lowercase` (bool) = True
- `remove_accents` (bool) = True

**Returns:**

- str


### `convert_case(text: str, case_type: str) -> str`

Convert text to specified case format.

Supported formats:
- "upper": ALL UPPERCASE
- "lower": all lowercase
- "title": Title Case
- "snake": snake_case
- "camel": camelCase

Args:
    text: Input text to convert
    case_type: Target case format (upper, lower, title, snake, camel)
    
Returns:
    Text converted to specified case
    
Raises:
    ValueError: If case_type is not supported

**Parameters:**

- `text` (str)
- `case_type` (str)

**Returns:**

- str


### `remove_special_chars(text: str, keep_alphanumeric: bool = True) -> str`

Remove special characters from text.

Args:
    text: Input text
    keep_alphanumeric: Keep alphanumeric characters. Defaults to True
    
Returns:
    Text with special characters removed

**Parameters:**

- `text` (str)
- `keep_alphanumeric` (bool) = True

**Returns:**

- str


### `slugify(text: str, separator: str = '-') -> str`

Convert text to a URL-friendly slug.

Args:
    text: Input text
    separator: Character to use as word separator. Defaults to "-"
    
Returns:
    Slugified text

**Parameters:**

- `text` (str)
- `separator` (str) = '-'

**Returns:**

- str

