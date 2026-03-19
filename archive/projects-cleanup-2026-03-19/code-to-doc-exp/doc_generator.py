"""
Markdown documentation generator from AST analysis results.

Generates formatted documentation for functions and classes.
"""

from typing import List, Optional
import time
from ast_analyzer import FunctionInfo, ClassInfo, Parameter


class MarkdownGenerator:
    """Generate Markdown documentation from function and class info."""
    
    @staticmethod
    def generate_function_doc(func: FunctionInfo, include_source: bool = False) -> str:
        """
        Generate Markdown documentation for a function.
        
        Args:
            func: FunctionInfo object
            include_source: Include source code in documentation
            
        Returns:
            Markdown formatted documentation
        """
        lines = []
        
        # Function signature
        signature = func.get_signature()
        lines.append(f"### `{signature}`")
        lines.append("")
        
        # Docstring
        if func.docstring:
            lines.append(func.docstring)
        else:
            lines.append("_No documentation provided._")
        lines.append("")
        
        # Parameters section (extracted from docstring or from signature)
        if func.parameters:
            lines.append("**Parameters:**")
            lines.append("")
            for param in func.parameters:
                annotation = f" ({param.annotation})" if param.annotation else ""
                default = f" = {param.default}" if param.default else ""
                lines.append(f"- `{param.name}`{annotation}{default}")
            lines.append("")
        
        # Return type
        if func.return_annotation:
            lines.append("**Returns:**")
            lines.append("")
            lines.append(f"- {func.return_annotation}")
            lines.append("")
        
        # Source code (optional)
        if include_source and func.source_code:
            lines.append("**Source:**")
            lines.append("")
            lines.append(f"```python")
            lines.append(func.source_code)
            lines.append("```")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_class_doc(cls: ClassInfo, include_methods: bool = True) -> str:
        """
        Generate Markdown documentation for a class.
        
        Args:
            cls: ClassInfo object
            include_methods: Include public methods
            
        Returns:
            Markdown formatted documentation
        """
        lines = []
        
        # Class header
        bases = ", ".join(cls.base_classes) if cls.base_classes else ""
        if bases:
            lines.append(f"## class `{cls.name}({bases})`")
        else:
            lines.append(f"## class `{cls.name}`")
        lines.append("")
        
        # Docstring
        if cls.docstring:
            lines.append(cls.docstring)
        else:
            lines.append("_No documentation provided._")
        lines.append("")
        
        # Methods
        if include_methods:
            public_methods = cls.public_methods()
            if public_methods:
                lines.append("### Methods")
                lines.append("")
                
                for method in public_methods:
                    method_doc = MarkdownGenerator.generate_function_doc(method)
                    lines.append(method_doc)
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_module_doc(module_name: str, 
                          functions: List[FunctionInfo],
                          classes: List[ClassInfo]) -> str:
        """
        Generate Markdown documentation for a module.
        
        Args:
            module_name: Module name
            functions: List of public functions
            classes: List of classes
            
        Returns:
            Complete Markdown documentation
        """
        lines = []
        
        # Module header
        lines.append(f"# Module `{module_name}`")
        lines.append("")
        lines.append("")
        
        # Classes
        if classes:
            lines.append("## Classes")
            lines.append("")
            for cls in classes:
                lines.append(MarkdownGenerator.generate_class_doc(cls))
                lines.append("")
        
        # Functions
        public_funcs = [f for f in functions if not f.is_private]
        if public_funcs:
            lines.append("## Functions")
            lines.append("")
            for func in public_funcs:
                lines.append(MarkdownGenerator.generate_function_doc(func))
                lines.append("")
        
        return "\n".join(lines)


class DocumentationGenerator:
    """Main documentation generator."""
    
    def __init__(self):
        self.generation_times = []
    
    def generate_all_modules(self, module_dict) -> dict:
        """
        Generate documentation for all modules.
        
        Args:
            module_dict: Dictionary of module data
            
        Returns:
            Dictionary mapping module name to generated markdown
        """
        results = {}
        
        for module_name, (functions, classes) in module_dict.items():
            start = time.time()
            doc = MarkdownGenerator.generate_module_doc(
                module_name.replace('.py', '').replace('/', '.'),
                functions,
                classes
            )
            elapsed = (time.time() - start) * 1000
            self.generation_times.append(elapsed)
            
            results[module_name] = doc
        
        return results
    
    def get_stats(self) -> dict:
        """Get generation statistics."""
        if not self.generation_times:
            return {}
        
        total = sum(self.generation_times)
        return {
            "total_time_ms": total,
            "avg_time_ms": total / len(self.generation_times),
            "min_time_ms": min(self.generation_times),
            "max_time_ms": max(self.generation_times),
            "num_modules": len(self.generation_times),
        }
