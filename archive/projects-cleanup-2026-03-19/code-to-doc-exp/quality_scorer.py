"""
Quality assessment for generated documentation.

Evaluates documentation on completeness, accuracy, clarity, and consistency.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import re


@dataclass
class QualityScore:
    """Represents a quality assessment."""
    completeness: float  # 0-100
    clarity: float       # 0-100
    consistency: float   # 0-100
    overall: float       # 0-100
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class QualityAssessor:
    """Assess documentation quality."""
    
    @staticmethod
    def assess_function_doc(doc: str, func_name: str) -> QualityScore:
        """
        Assess quality of function documentation.
        
        Args:
            doc: Generated documentation
            func_name: Function name
            
        Returns:
            QualityScore object
        """
        issues = []
        scores = {}
        
        # COMPLETENESS: Check for presence of key sections
        has_docstring = bool(doc)
        has_params = "Parameters:" in doc or "Args:" in doc
        has_returns = "Returns:" in doc or "Return" in doc
        has_examples = "Examples:" in doc or "Example:" in doc
        
        completeness_score = 0
        if has_docstring:
            completeness_score += 25
        if has_params:
            completeness_score += 25
        if has_returns:
            completeness_score += 25
        if has_examples:
            completeness_score += 25
        
        if not has_params:
            issues.append(f"Missing parameter documentation")
        if not has_returns:
            issues.append(f"Missing return type documentation")
        if not has_examples:
            issues.append(f"Missing usage examples")
        
        scores['completeness'] = min(100, completeness_score)
        
        # CLARITY: Check for code quality indicators
        clarity_score = 50  # Base score
        
        # Check for type hints
        has_type_hints = "::" in doc or "(" in doc and ")" in doc
        if has_type_hints:
            clarity_score += 20
        
        # Check for descriptive text
        words = len(doc.split())
        if words > 50:
            clarity_score += 15
        elif words > 20:
            clarity_score += 10
        
        # Check for formatting
        has_code_blocks = "```" in doc
        if has_code_blocks:
            clarity_score += 15
        
        scores['clarity'] = min(100, clarity_score)
        
        # CONSISTENCY: Check for consistent formatting
        consistency_score = 50  # Base score
        
        # Check heading consistency
        if doc.count("###") > 0:
            consistency_score += 10
        
        # Check list consistency  
        if doc.count("- ") > 0:
            consistency_score += 10
        
        # Check code formatting
        if "```" in doc:
            consistency_score += 10
        
        # Check description length consistency
        lines = [l.strip() for l in doc.split('\n') if l.strip()]
        if len(lines) > 3:
            consistency_score += 20
        
        scores['consistency'] = min(100, consistency_score)
        
        # OVERALL
        overall = (scores['completeness'] + scores['clarity'] + scores['consistency']) / 3
        
        return QualityScore(
            completeness=scores['completeness'],
            clarity=scores['clarity'],
            consistency=scores['consistency'],
            overall=overall,
            issues=issues,
        )
    
    @staticmethod
    def assess_module_doc(module_doc: str, expected_functions: int) -> QualityScore:
        """
        Assess quality of module documentation.
        
        Args:
            module_doc: Generated module documentation
            expected_functions: Expected number of functions
            
        Returns:
            QualityScore object
        """
        issues = []
        scores = {}
        
        # COMPLETENESS: Document coverage
        coverage_score = 50
        
        # Check for module header
        if "# Module" in module_doc:
            coverage_score += 15
        
        # Count documented functions
        func_count = module_doc.count("###")
        if func_count >= expected_functions * 0.8:
            coverage_score += 25
        elif func_count >= expected_functions * 0.5:
            coverage_score += 15
        else:
            coverage_score += 5
            issues.append(f"Low function coverage ({func_count}/{expected_functions})")
        
        scores['completeness'] = min(100, coverage_score)
        
        # CLARITY
        clarity_score = 50
        
        # Check document length
        doc_length = len(module_doc)
        if doc_length > 5000:
            clarity_score += 20
        elif doc_length > 2000:
            clarity_score += 10
        
        # Check organization
        has_sections = module_doc.count("##") > 0
        if has_sections:
            clarity_score += 20
        
        # Check code examples
        has_examples = "```" in module_doc
        if has_examples:
            clarity_score += 10
        
        scores['clarity'] = min(100, clarity_score)
        
        # CONSISTENCY
        consistency_score = 50
        
        # Check consistent formatting
        lines = module_doc.split('\n')
        formatted_lines = [l for l in lines if l.startswith('#') or l.startswith('-') or l.startswith('`')]
        if formatted_lines:
            consistency_score += 25
        
        # Check section structure
        has_functions_section = "## Functions" in module_doc
        has_classes_section = "## Classes" in module_doc
        if has_functions_section or has_classes_section:
            consistency_score += 15
        
        scores['consistency'] = min(100, consistency_score)
        
        # OVERALL
        overall = (scores['completeness'] + scores['clarity'] + scores['consistency']) / 3
        
        return QualityScore(
            completeness=scores['completeness'],
            clarity=scores['clarity'],
            consistency=scores['consistency'],
            overall=overall,
            issues=issues,
        )


class QualityComparator:
    """Compare generated documentation with reference documentation."""
    
    @staticmethod
    def compare_docs(generated: str, reference: str) -> Dict:
        """
        Compare generated and reference documentation.
        
        Args:
            generated: Generated documentation
            reference: Reference documentation
            
        Returns:
            Comparison results dictionary
        """
        results = {
            'similarity': 0.0,
            'missing_sections': [],
            'extra_sections': [],
            'length_diff_percent': 0.0,
        }
        
        # Length comparison
        ref_len = len(reference)
        gen_len = len(generated)
        if ref_len > 0:
            results['length_diff_percent'] = ((gen_len - ref_len) / ref_len) * 100
        
        # Section comparison
        ref_sections = set(re.findall(r'^#+\s+(.+)$', reference, re.MULTILINE))
        gen_sections = set(re.findall(r'^#+\s+(.+)$', generated, re.MULTILINE))
        
        results['missing_sections'] = list(ref_sections - gen_sections)
        results['extra_sections'] = list(gen_sections - ref_sections)
        
        # Simple similarity (Jaccard index on words)
        ref_words = set(reference.lower().split())
        gen_words = set(generated.lower().split())
        
        if ref_words or gen_words:
            intersection = len(ref_words & gen_words)
            union = len(ref_words | gen_words)
            results['similarity'] = (intersection / union) * 100 if union > 0 else 0
        
        return results


def evaluate_all_docs(module_docs: Dict[str, str], 
                     function_counts: Dict[str, int]) -> Dict:
    """
    Evaluate all generated documentation.
    
    Args:
        module_docs: Dictionary of generated module documentation
        function_counts: Dictionary of expected function counts per module
        
    Returns:
        Comprehensive evaluation results
    """
    results = {}
    overall_scores = []
    
    for module_name, doc in module_docs.items():
        expected_funcs = function_counts.get(module_name, 0)
        score = QualityAssessor.assess_module_doc(doc, expected_funcs)
        
        results[module_name] = {
            'completeness': score.completeness,
            'clarity': score.clarity,
            'consistency': score.consistency,
            'overall': score.overall,
            'issues': score.issues,
        }
        
        overall_scores.append(score.overall)
    
    # Calculate averages
    if overall_scores:
        avg_overall = sum(overall_scores) / len(overall_scores)
        results['_summary'] = {
            'avg_overall': avg_overall,
            'avg_completeness': sum(r['completeness'] for r in results.values() if r != '_summary') / (len(results) - 1),
            'avg_clarity': sum(r['clarity'] for r in results.values() if r != '_summary') / (len(results) - 1),
            'avg_consistency': sum(r['consistency'] for r in results.values() if r != '_summary') / (len(results) - 1),
        }
    
    return results
