# Module `logging_utils`


## Classes

## class `ColorFormatter(logging.Formatter)`

Custom formatter with color support for console output.

### Methods

### `format(self, record: logging.LogRecord) -> str`

Format log record with color.

**Parameters:**

- `self`
- `record` (logging.LogRecord)

**Returns:**

- str


## Functions

### `setup_logger(name: str, level: str = 'INFO', log_file: Optional[str] = None, format_string: Optional[str] = None) -> logging.Logger`

Setup a configured logger with console and optional file output.

Args:
    name: Logger name
    level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    log_file: Optional file path to write logs
    format_string: Custom format string for log messages
    
Returns:
    Configured logger instance

**Parameters:**

- `name` (str)
- `level` (str) = 'INFO'
- `log_file` (Optional[str]) = None
- `format_string` (Optional[str]) = None

**Returns:**

- logging.Logger


### `log_performance(func)`

Decorator to log function execution time and arguments.

Args:
    func: Function to decorate
    
Returns:
    Decorated function

**Parameters:**

- `func`


### `wrapper()`

_No documentation provided._

