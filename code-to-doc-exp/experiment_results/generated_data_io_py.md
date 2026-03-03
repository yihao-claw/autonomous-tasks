# Module `data_io`


## Functions

### `load_csv(filepath: str, delimiter: str = ',', skip_header: bool = False) -> List[Dict[(str, str)]]`

Load data from a CSV file and return as a list of dictionaries.

Args:
    filepath: Path to the CSV file
    delimiter: Field delimiter character. Defaults to ","
    skip_header: Skip the first row. Defaults to False
    
Returns:
    List of dictionaries where keys are column names
    
Raises:
    FileNotFoundError: If file does not exist
    csv.Error: If CSV parsing fails

**Parameters:**

- `filepath` (str)
- `delimiter` (str) = ','
- `skip_header` (bool) = False

**Returns:**

- List[Dict[(str, str)]]


### `save_csv(data: List[Dict[(str, Any)]], filepath: str, delimiter: str = ',') -> None`

Save a list of dictionaries to a CSV file.

Args:
    data: List of dictionaries to save
    filepath: Output file path
    delimiter: Field delimiter character. Defaults to ","
    
Raises:
    ValueError: If data is empty or has inconsistent keys

**Parameters:**

- `data` (List[Dict[(str, Any)]])
- `filepath` (str)
- `delimiter` (str) = ','

**Returns:**

- None


### `load_json(filepath: str) -> Any`

Load JSON data from a file.

Args:
    filepath: Path to the JSON file
    
Returns:
    Parsed JSON data (dict, list, or primitive)
    
Raises:
    FileNotFoundError: If file does not exist
    json.JSONDecodeError: If JSON is invalid

**Parameters:**

- `filepath` (str)

**Returns:**

- Any


### `save_json(data: Any, filepath: str, indent: int = 2, sort_keys: bool = False) -> None`

Save data to a JSON file.

Args:
    data: Data to save (must be JSON serializable)
    filepath: Output file path
    indent: JSON indentation level. Defaults to 2
    sort_keys: Sort object keys in output. Defaults to False
    
Raises:
    TypeError: If data is not JSON serializable

**Parameters:**

- `data` (Any)
- `filepath` (str)
- `indent` (int) = 2
- `sort_keys` (bool) = False

**Returns:**

- None

