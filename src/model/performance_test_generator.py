#!/usr/bin/env python3
"""
Performance Test Generator
Generates performance test files for Python functions with runtime and memory profiling.
"""

import ast
import re
import json
from typing import Dict, List, Optional, Tuple
import textwrap


class PerformanceTestGenerator:
    """Generates performance tests for Python functions."""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Returns the template for performance tests."""
        return '''# -*- coding: utf-8 -*-
"""
Auto-generated Performance Test
Generated for: {function_name}
Predicted Complexity: {complexity}
"""

import time
import tracemalloc
import sys
from typing import List, Tuple, Callable
import matplotlib.pyplot as plt
import numpy as np


# ============ ORIGINAL FUNCTION ============
{original_code}


# ============ TEST DATA GENERATORS ============
{data_generators}


# ============ PERFORMANCE TESTING FRAMEWORK ============
class PerformanceTester:
    """Framework for measuring runtime and memory usage."""
    
    def __init__(self, func: Callable, complexity: str):
        self.func = func
        self.complexity = complexity
        self.results = []
    
    def measure_performance(self, input_data, runs: int = 5) -> Tuple[float, float]:
        """
        Measure average runtime and peak memory for a single input.
        
        Args:
            input_data: Input to pass to the function
            runs: Number of times to run for averaging
        
        Returns:
            Tuple of (average_time_ms, peak_memory_kb)
        """
        times = []
        memories = []
        
        for _ in range(runs):
            # Measure memory
            tracemalloc.start()
            
            # Measure time
            start_time = time.perf_counter()
            if isinstance(input_data, tuple):
                self.func(*input_data)
            else:
                self.func(input_data)
            end_time = time.perf_counter()
            
            # Get memory stats
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            times.append((end_time - start_time) * 1000)  # Convert to ms
            memories.append(peak / 1024)  # Convert to KB
        
        avg_time = sum(times) / len(times)
        avg_memory = sum(memories) / len(memories)
        
        return avg_time, avg_memory
    
    def run_tests(self, test_sizes: List[int], data_generator: Callable) -> None:
        """
        Run performance tests across different input sizes.
        
        Args:
            test_sizes: List of input sizes to test
            data_generator: Function that generates test data given a size
        """
        print("\\n" + "=" * 60)
        print(f"Performance Testing: {{self.func.__name__}}")
        print(f"Predicted Complexity: {{self.complexity}}")
        print("=" * 60 + "\\n")
        
        self.results = []
        
        for size in test_sizes:
            print(f"Testing with input size: {{size}}...", end=" ")
            test_data = data_generator(size)
            
            avg_time, avg_memory = self.measure_performance(test_data)
            
            self.results.append({{
                'size': size,
                'time_ms': avg_time,
                'memory_kb': avg_memory
            }})
            
            print(f"Time: {{avg_time:.4f}}ms, Memory: {{avg_memory:.2f}}KB")
        
        print("\\n" + "=" * 60 + "\\n")
    
    def display_results(self) -> None:
        """Display test results in a formatted table."""
        print("\\nDetailed Results:")
        print(f"{{'Input Size':<15}} {{'Time (ms)':<20}} {{'Memory (KB)':<20}}")
        print("-" * 60)
        
        for result in self.results:
            print(f"{{result['size']:<15}} {{result['time_ms']:<20.4f}} {{result['memory_kb']:<20.2f}}")
    
    def plot_results(self, save_path: str = None) -> None:
        """
        Generate performance visualization plots.
        
        Args:
            save_path: Optional path to save the plot image
        """
        if not self.results:
            print("No results to plot!")
            return
        
        sizes = [r['size'] for r in self.results]
        times = [r['time_ms'] for r in self.results]
        memories = [r['memory_kb'] for r in self.results]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Runtime plot
        ax1.plot(sizes, times, 'b-o', linewidth=2, markersize=8)
        ax1.set_xlabel('Input Size (n)', fontsize=12)
        ax1.set_ylabel('Time (ms)', fontsize=12)
        ax1.set_title(f'Runtime Analysis\\nPredicted: {{self.complexity}}', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Memory plot
        ax2.plot(sizes, memories, 'r-s', linewidth=2, markersize=8)
        ax2.set_xlabel('Input Size (n)', fontsize=12)
        ax2.set_ylabel('Memory (KB)', fontsize=12)
        ax2.set_title(f'Memory Usage Analysis', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\\nPlot saved to: {{save_path}}")
        
        plt.show()
    
    def analyze_complexity(self) -> str:
        """
        Analyze actual complexity based on measured results.
        
        Returns:
            String describing the empirical complexity
        """
        if len(self.results) < 3:
            return "Insufficient data for complexity analysis"
        
        sizes = np.array([r['size'] for r in self.results])
        times = np.array([r['time_ms'] for r in self.results])
        
        # Normalize
        sizes_norm = sizes / sizes[0]
        times_norm = times / times[0]
        
        # Calculate growth ratios
        ratios = []
        for i in range(1, len(sizes_norm)):
            size_ratio = sizes_norm[i] / sizes_norm[i-1]
            time_ratio = times_norm[i] / times_norm[i-1]
            if size_ratio > 1:
                ratios.append(time_ratio / size_ratio)
        
        if not ratios:
            return "Unable to determine complexity"
        
        avg_ratio = np.mean(ratios)
        
        # Classify complexity
        if avg_ratio < 1.2:
            empirical = "O(1) or O(log n)"
        elif 1.2 <= avg_ratio < 1.8:
            empirical = "O(n)"
        elif 1.8 <= avg_ratio < 3.0:
            empirical = "O(n log n)"
        elif 3.0 <= avg_ratio < 5.0:
            empirical = "O(n²)"
        else:
            empirical = "O(n³) or higher"
        
        return f"Empirical: {{empirical}} (predicted: {{self.complexity}})"


# ============ RUN TESTS ============
if __name__ == "__main__":
    # Configure test parameters
    test_sizes = {test_sizes}
    
    # Create tester
    tester = PerformanceTester({function_name}, "{complexity}")
    
    # Run tests
    tester.run_tests(test_sizes, {data_generator_name})
    
    # Display results
    tester.display_results()
    
    # Analyze complexity
    print(f"\\nComplexity Analysis: {{tester.analyze_complexity()}}")
    
    # Generate plots
    try:
        tester.plot_results(save_path="{function_name}_performance.png")
    except Exception as e:
        print(f"\\nNote: Could not generate plots: {{e}}")
        print("Install matplotlib with: pip install matplotlib")
'''
    
    def extract_function_info(self, code: str) -> Optional[Dict]:
        """
        Extract function information from code.
        
        Args:
            code: Python source code
        
        Returns:
            Dictionary with function info or None if no function found
        """
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function name
                    func_name = node.name
                    
                    # Get parameters
                    params = [arg.arg for arg in node.args.args]
                    
                    # Get function body
                    func_code = ast.get_source_segment(code, node)
                    
                    return {
                        'name': func_name,
                        'params': params,
                        'code': func_code or code,
                        'has_list_param': any('arr' in p or 'list' in p or 'array' in p for p in params),
                        'has_n_param': 'n' in params
                    }
        except Exception as e:
            print(f"Error parsing code: {e}")
            return None
    
    def infer_data_generator(self, func_info: Dict, complexity: str) -> Tuple[str, str]:
        """
        Infer appropriate data generator based on function signature.
        
        Args:
            func_info: Function information dictionary
            complexity: Predicted complexity
        
        Returns:
            Tuple of (generator_code, generator_name)
        """
        params = func_info['params']
        func_name = func_info['name']
        
        # Detect function type based on parameters and name
        # Check for 2-parameter functions first (more specific)
        if len(params) == 2 and func_info['has_list_param']:
            # Array with target (e.g., search functions)
            generator_code = '''def generate_list_with_target(size: int):
    """Generate a sorted list with a target value (for search functions)."""
    import random
    arr = sorted([random.randint(1, 1000) for _ in range(size)])
    target = arr[size // 2] if arr else 0
    return (arr, target)
'''
            generator_name = "generate_list_with_target"
        
        elif func_info['has_list_param'] or 'sort' in func_name:
            # Array/list based function (single parameter)
            generator_code = '''def generate_list_input(size: int):
    """Generate a random list of integers."""
    import random
    return [random.randint(1, 1000) for _ in range(size)]
'''
            generator_name = "generate_list_input"
            
        elif func_info['has_n_param'] or 'fib' in func_name or 'factorial' in func_name:
            # Integer input function
            generator_code = '''def generate_integer_input(size: int):
    """Generate integer input."""
    return size
'''
            generator_name = "generate_integer_input"
            
        elif 'matrix' in func_name.lower():
            # Matrix operations
            generator_code = '''def generate_matrix_input(size: int):
    """Generate random square matrices."""
    import random
    matrix_a = [[random.randint(1, 10) for _ in range(size)] for _ in range(size)]
    matrix_b = [[random.randint(1, 10) for _ in range(size)] for _ in range(size)]
    return (matrix_a, matrix_b)
'''
            generator_name = "generate_matrix_input"
            
        else:
            # Default: list input
            generator_code = '''def generate_input(size: int):
    """Generate input data for testing."""
    import random
    return [random.randint(1, 1000) for _ in range(size)]
'''
            generator_name = "generate_input"
        
        return generator_code, generator_name
    
    def infer_test_sizes(self, complexity: str) -> List[int]:
        """
        Infer appropriate test sizes based on complexity.
        
        Args:
            complexity: Predicted time complexity
        
        Returns:
            List of test sizes
        """
        complexity_lower = complexity.lower()
        
        if 'n^3' in complexity_lower or 'n³' in complexity_lower:
            return [10, 20, 30, 50, 75, 100]
        elif 'n^2' in complexity_lower or 'n²' in complexity_lower:
            return [10, 50, 100, 200, 500, 1000]
        elif 'n log n' in complexity_lower or 'nlogn' in complexity_lower:
            return [100, 500, 1000, 5000, 10000, 50000]
        elif 'log n' in complexity_lower or 'log(n)' in complexity_lower:
            return [1000, 10000, 100000, 1000000]
        else:  # O(n) or O(1)
            return [100, 1000, 5000, 10000, 50000, 100000]
    
    def generate_test_file(self, code: str, complexity: str) -> Optional[str]:
        """
        Generate complete performance test file.
        
        Args:
            code: Original function code
            complexity: Predicted complexity from model
        
        Returns:
            Complete test file as string, or None if generation fails
        """
        # Extract function info
        func_info = self.extract_function_info(code)
        if not func_info:
            return None
        
        # Generate data generator
        data_gen_code, data_gen_name = self.infer_data_generator(func_info, complexity)
        
        # Determine test sizes
        test_sizes = self.infer_test_sizes(complexity)
        
        # Fill template
        test_file = self.template.format(
            function_name=func_info['name'],
            complexity=complexity,
            original_code=textwrap.indent(func_info['code'], ''),
            data_generators=data_gen_code,
            test_sizes=test_sizes,
            data_generator_name=data_gen_name
        )
        
        return test_file


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python performance_test_generator.py <code_file> <complexity>")
        print("Example: python performance_test_generator.py my_func.py 'O(n^2)'")
        sys.exit(1)
    
    code_file = sys.argv[1]
    complexity = sys.argv[2]
    
    with open(code_file, 'r') as f:
        code = f.read()
    
    generator = PerformanceTestGenerator()
    test_file = generator.generate_test_file(code, complexity)
    
    if test_file:
        output_file = code_file.replace('.py', '_performance_test.py')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_file)
        print(f"✅ Performance test generated: {output_file}")
    else:
        print("❌ Failed to generate test file")

