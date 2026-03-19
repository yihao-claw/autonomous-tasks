"""
AST-based Python code analyzer for automatic documentation generation.

Extracts functions, classes, parameters, type hints, and docstrings.
"""

import ast
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import time


@dataclass
class Parameter:
    """Represents a function parameter."""
    name: str
    annotation: Optional[str] = None
    default: Optional[str] = None
    
    def __repr__(self) -> str:
        parts = [self.name]
        if self.annotation:
            parts.append(f": {self.annotation}")
        if self.default:
            parts.append(f" = {self.default}")
        return "".join(parts)


@dataclass
class FunctionInfo:
    """Represents extracted function information."""
    name: str
    module: str
    lineno: int
    docstring: Optional[str] = None
    parameters: List[Parameter] = field(default_factory=list)
    return_annotation: Optional[str] = None
    is_method: bool = False
    is_private: bool = False
    source_code: Optional[str] = None
    
    def get_signature(self) -> str:
        """Get function signature."""
        params_str = ", ".join(str(p) for p in self.parameters)
        ret = f" -> {self.return_annotation}" if self.return_annotation else ""
        return f"{self.name}({params_str}){ret}"


@dataclass
class ClassInfo:
    """Represents extracted class information."""
    name: str
    module: str
    lineno: int
    docstring: Optional[str] = None
    methods: List[FunctionInfo] = field(default_factory=list)
    base_classes: List[str] = field(default_factory=list)
    
    def public_methods(self) -> List[FunctionInfo]:
        """Get all public methods."""
        return [m for m in self.methods if not m.is_private]


class ASTAnalyzer(ast.NodeVisitor):
    """AST visitor to extract function and class information."""
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.functions: List[FunctionInfo] = []
        self.classes: List[ClassInfo] = []
        self.current_class: Optional[ClassInfo] = None
        self.source_lines: Dict[int, str] = {}
    
    def set_source_lines(self, lines: List[str]) -> None:
        """Store source lines for reference."""
        self.source_lines = {i + 1: line for i, line in enumerate(lines)}
    
    def _get_annotation_string(self, annotation: Optional[ast.expr]) -> Optional[str]:
        """Convert annotation AST node to string."""
        if annotation is None:
            return None
        
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            value = self._get_annotation_string(annotation.value)
            slice_str = self._get_annotation_string(annotation.slice)
            return f"{value}[{slice_str}]"
        elif isinstance(annotation, ast.Tuple):
            elements = [self._get_annotation_string(e) for e in annotation.elts]
            return f"({', '.join(e for e in elements if e)})"
        elif isinstance(annotation, ast.List):
            elements = [self._get_annotation_string(e) for e in annotation.elts]
            return f"[{', '.join(e for e in elements if e)}]"
        elif isinstance(annotation, ast.Attribute):
            value = self._get_annotation_string(annotation.value)
            return f"{value}.{annotation.attr}"
        else:
            return ast.unparse(annotation) if hasattr(ast, 'unparse') else None
    
    def _get_default_string(self, default: Optional[ast.expr]) -> Optional[str]:
        """Convert default value AST node to string."""
        if default is None:
            return None
        
        if isinstance(default, ast.Constant):
            return repr(default.value)
        elif isinstance(default, ast.Name):
            return default.id
        else:
            return ast.unparse(default) if hasattr(ast, 'unparse') else "..."
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definition."""
        # Extract parameters
        parameters = []
        for arg in node.args.args:
            annotation = self._get_annotation_string(arg.annotation)
            parameters.append(Parameter(name=arg.arg, annotation=annotation))
        
        # Add defaults (align with the last parameters)
        num_defaults = len(node.args.defaults)
        for i, default in enumerate(node.args.defaults):
            param_idx = len(parameters) - num_defaults + i
            if param_idx >= 0:
                parameters[param_idx].default = self._get_default_string(default)
        
        # Extract return annotation
        return_annotation = self._get_annotation_string(node.returns)
        
        # Extract docstring
        docstring = ast.get_docstring(node)
        
        # Get source code snippet
        source_code = None
        if node.lineno in self.source_lines:
            source_code = self.source_lines.get(node.lineno, "")
        
        # Create function info
        func_info = FunctionInfo(
            name=node.name,
            module=self.module_name,
            lineno=node.lineno,
            docstring=docstring,
            parameters=parameters,
            return_annotation=return_annotation,
            is_method=self.current_class is not None,
            is_private=node.name.startswith('_'),
            source_code=source_code,
        )
        
        if self.current_class:
            self.current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definition."""
        # Treat as regular function for now
        self.visit_FunctionDef(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition."""
        # Get base classes
        base_classes = [self._get_annotation_string(base) or str(base) for base in node.bases]
        
        # Get docstring
        docstring = ast.get_docstring(node)
        
        # Create class info
        class_info = ClassInfo(
            name=node.name,
            module=self.module_name,
            lineno=node.lineno,
            docstring=docstring,
            base_classes=base_classes,
        )
        
        # Visit methods
        prev_class = self.current_class
        self.current_class = class_info
        
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(item)
        
        self.current_class = prev_class
        self.classes.append(class_info)


def analyze_file(filepath: str) -> Tuple[List[FunctionInfo], List[ClassInfo], float]:
    """
    Analyze a Python file and extract function/class information.
    
    Args:
        filepath: Path to Python file
        
    Returns:
        Tuple of (functions, classes, analysis_time_ms)
    """
    start_time = time.time()
    
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
        lines = source.split('\n')
    
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise ValueError(f"Syntax error in {filepath}: {e}")
    
    # Get module name from filename
    module_name = path.stem
    
    # Analyze
    analyzer = ASTAnalyzer(module_name)
    analyzer.set_source_lines(lines)
    analyzer.visit(tree)
    
    elapsed_ms = (time.time() - start_time) * 1000
    return analyzer.functions, analyzer.classes, elapsed_ms


def analyze_directory(directory: str) -> Dict[str, Tuple[List[FunctionInfo], List[ClassInfo]]]:
    """
    Analyze all Python files in a directory.
    
    Args:
        directory: Path to directory
        
    Returns:
        Dictionary mapping filename to (functions, classes)
    """
    results = {}
    path = Path(directory)
    
    for py_file in path.glob('**/*.py'):
        if py_file.name.startswith('_'):
            continue
        
        try:
            functions, classes, _ = analyze_file(str(py_file))
            rel_path = str(py_file.relative_to(path))
            results[rel_path] = (functions, classes)
        except Exception as e:
            print(f"Warning: Failed to analyze {py_file}: {e}")
    
    return results
