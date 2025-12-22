# Usage Instructions:
# ollama serve
# python src/generate_data.py --categories <category> --delay <sec>
# Note: The number of samples per category is automatically taken from ComplexityCategory[category]["target_count"]


import subprocess, json, os, random, time, argparse, hashlib, requests
from pathlib import Path

# === Paths ===
PROMPT_PATH = Path("data/prompts/prompt.txt")
OUTPUT_PATH = Path("data/raw/generated.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# === Category & variation configuration ===

ComplexityCategory = {
    "basic_loops": {
        "subcategories": [
            "single_loop", "nested_2_loops", "nested_3_loops",
            "sequential_loops", "loop_with_break", "loop_with_continue"
        ],
        "target_count": 800
    },
    "recursion": {
        "subcategories": [
            "linear_recursion", "binary_recursion", "tree_recursion",
            "tail_recursion", "mutual_recursion", "memoized_recursion"
        ],
        "target_count": 1000
    },
    "searching": {
        "subcategories": [
            "linear_search", "binary_search", "interpolation_search",
            "exponential_search", "ternary_search"
        ],
        "target_count": 600
    },
    "sorting": {
        "subcategories": [
            "bubble_sort", "selection_sort", "insertion_sort",
            "merge_sort", "quick_sort", "heap_sort", "counting_sort",
            "radix_sort", "bucket_sort"
        ],
        "target_count": 900
    },
    "data_structures": {
        "subcategories": [
            "array_operations", "linked_list_ops", "stack_ops",
            "queue_ops", "hash_table_ops", "tree_ops", "graph_ops",
            "heap_ops", "trie_ops"
        ],
        "target_count": 1500
    },
    "dynamic_programming": {
        "subcategories": [
            "fibonacci_variants", "knapsack_variants", "lcs_variants",
            "matrix_chain", "coin_change", "edit_distance"
        ],
        "target_count": 1000
    },
    "graph_algorithms": {
        "subcategories": [
            "dfs", "bfs", "dijkstra", "bellman_ford", "floyd_warshall",
            "prims", "kruskals", "topological_sort"
        ],
        "target_count": 800
    },
    "string_algorithms": {
        "subcategories": [
            "pattern_matching", "string_manipulation", "suffix_arrays",
            "kmp", "rabin_karp", "longest_palindrome"
        ],
        "target_count": 600
    },
    "divide_and_conquer": {
        "subcategories": [
            "binary_search_variants", "merge_operations", "quickselect",
            "strassen", "closest_pair"
        ],
        "target_count": 500
    },
    "greedy_algorithms": {
        "subcategories": [
            "activity_selection", "huffman_coding", "interval_scheduling",
            "fractional_knapsack", "job_scheduling"
        ],
        "target_count": 500
    },
    "mathematical": {
        "subcategories": [
            "number_theory", "combinatorics", "prime_algorithms",
            "gcd_lcm", "modular_arithmetic", "matrix_operations"
        ],
        "target_count": 600
    },
    "stdlib_operations": {
        "subcategories": [
            "list_comprehensions", "dict_operations", "set_operations",
            "itertools_usage", "collections_usage", "functools_usage"
        ],
        "target_count": 1200
    }
}

_VARIATIONS = {
    "basic_loops": [
        "Use range with start, stop, step",
        "Use enumerate for index tracking",
        "Use zip for parallel iteration",
        "Use list comprehension where appropriate",
        "Use traditional for loop with counter",
        "Use while loop with manual counter increment",
        "Use reversed() for backward iteration",
        "Implement using itertools.cycle or repeat",
        "Use nested loops with early break optimization",
        "Combine multiple loop conditions with and/or",
        "Use slice notation for efficient iteration",
        "Implement with loop unrolling for small iterations",
        "Use generator expressions for memory efficiency",
        "Include loop invariant comments",
        "Use range with negative step for countdown",
        "Implement with continue for skipping iterations",
        "Use all() or any() for loop termination checks",
        "Combine with filter() for conditional iteration",
        "Use itertools.islice for bounded iteration",
        "Implement with manual index manipulation",
    ],
    
    "recursion": [
        "Implement with base case and recursive case clearly separated",
        "Use helper function with accumulator parameter",
        "Implement with multiple base cases",
        "Use wrapper function for cleaner interface",
        "Include tail call optimization opportunity",
        "Add memoization decorator for optimization",
        "Use lru_cache from functools",
        "Implement with explicit recursion depth tracking",
        "Include both recursive and iterative solutions for comparison",
        "Use mutual recursion between two functions",
        "Implement with stack simulation for tail recursion",
        "Add recursion depth limit checking",
        "Use divide and conquer approach",
        "Implement with forward and backward recursion",
        "Include recursive case analysis in comments",
        "Use parameter passing to avoid global state",
        "Implement with both top-down and bottom-up approaches",
        "Add visualization comments for recursion tree",
        "Use tuple unpacking in recursive calls",
        "Implement with continuation passing style",
    ],
    
    "searching": [
        "Implement with early termination on finding target",
        "Include detailed comparison count tracking",
        "Use sentinel values to optimize boundary checks",
        "Implement both recursive and iterative versions",
        "Add comprehensive docstring with complexity analysis",
        "Use bisect module for optimized binary search",
        "Include edge case handling for empty inputs",
        "Implement with left and right boundary tracking",
        "Use while loop with careful index management",
        "Add assertion checks for sorted array requirements",
        "Implement with exception handling for not found cases",
        "Use ternary operators for concise comparisons",
        "Include visualization of search space reduction",
        "Implement with generic comparator function parameter",
        "Add range validation for search bounds",
        "Use property-based testing examples in docstring",
        "Implement with both inclusive and exclusive bounds",
        "Include amortized analysis in comments",
        "Use type hints for input/output clarity",
        "Add benchmarking code in docstring examples",
    ],
    
    "sorting": [
        "Implement with in-place modification for O(1) space",
        "Use auxiliary array for stable sorting guarantee",
        "Include comparison count tracking for analysis",
        "Implement with three-way partitioning optimization",
        "Add adaptive behavior for nearly-sorted inputs",
        "Use sentinel values to eliminate boundary checks",
        "Implement with random pivot selection for quick sort",
        "Include hybrid approach (switch to insertion for small n)",
        "Use iterative bottom-up approach instead of recursive",
        "Add stability preservation with index tracking",
        "Implement with custom comparator function parameter",
        "Include optimization for duplicate elements",
        "Use bit manipulation for radix sort optimization",
        "Implement with parallel merge for large datasets",
        "Add early termination for already sorted input",
        "Use heapq module for heap sort implementation",
        "Include cache-friendly memory access patterns",
        "Implement with three-way comparison for efficiency",
        "Add detailed swap count and comparison metrics",
        "Use generator for lazy sorting when possible",
    ],
    
    "data_structures": [
        "Use list as underlying storage",
        "Use dict for O(1) lookup operations",
        "Use collections.deque for efficient operations",
        "Use heap for priority operations",
        "Use set for uniqueness constraints",
        "Implement with arrays and pointer manipulation",
        "Use collections.defaultdict for automatic initialization",
        "Implement with Node class for linked structures",
        "Use collections.Counter for frequency tracking",
        "Implement with both iterative and recursive traversal",
        "Use union-find with path compression",
        "Implement with lazy deletion for efficiency",
        "Use bisect for maintaining sorted invariant",
        "Implement with sentinel nodes to simplify edge cases",
        "Use weakref for memory-efficient caching",
        "Implement with copy-on-write optimization",
        "Use __slots__ for memory-efficient object storage",
        "Implement with bidirectional links for O(1) operations",
        "Use array.array for memory-efficient numeric storage",
        "Implement with amortized doubling for dynamic arrays",
        "Use OrderedDict when insertion order matters",
        "Implement with reference counting for garbage collection",
        "Use memoryview for efficient slicing without copies",
        "Implement with structural sharing for persistent structures",
    ],
    
    "dynamic_programming": [
        "Implement with 2D DP table for optimal substructure",
        "Use 1D array with rolling optimization for space efficiency",
        "Include both top-down (memoization) and bottom-up (tabulation)",
        "Add reconstruction path to show optimal solution",
        "Use dictionary for sparse state space",
        "Implement with state compression for reduced space",
        "Include detailed recurrence relation in comments",
        "Use lru_cache decorator for automatic memoization",
        "Implement with iterative space-optimized version",
        "Add visualization of DP table filling order",
        "Use tuple keys for multi-dimensional state",
        "Implement with forward and backward DP passes",
        "Include boundary condition handling explicitly",
        "Use sentinel values for initialization",
        "Implement with lazy evaluation of states",
        "Add pruning for unreachable states",
        "Use sliding window for constant space optimization",
        "Implement with path compression for optimal backtracking",
        "Include time-space tradeoff analysis in comments",
        "Use generators for memory-efficient state iteration",
    ],
    
    "graph_algorithms": [
        "Use adjacency list representation for sparse graphs",
        "Implement with adjacency matrix for dense graphs",
        "Include visited set for O(1) membership testing",
        "Use collections.deque for BFS queue operations",
        "Implement with priority queue for weighted graphs",
        "Add parent tracking for path reconstruction",
        "Use union-find for cycle detection in undirected graphs",
        "Implement with topological ordering for DAGs",
        "Include edge classification (tree, back, forward, cross)",
        "Use recursion stack simulation for iterative DFS",
        "Implement with bidirectional search optimization",
        "Add strongly connected components decomposition",
        "Use heap for Dijkstra's algorithm optimization",
        "Implement with negative cycle detection for Bellman-Ford",
        "Include cut vertex and bridge identification",
        "Use dynamic programming for all-pairs shortest paths",
        "Implement with A* heuristic for informed search",
        "Add minimum spanning tree property verification",
        "Use Tarjan's algorithm for efficient SCC finding",
        "Implement with iterative deepening for space efficiency",
    ],
    
    "string_algorithms": [
        "Use sliding window technique for substring problems",
        "Implement with two-pointer approach for palindromes",
        "Include rolling hash for efficient pattern matching",
        "Use trie data structure for prefix operations",
        "Implement with KMP failure function preprocessing",
        "Add Z-algorithm for linear time pattern matching",
        "Use suffix array with LCP for advanced queries",
        "Implement with Manacher's algorithm for palindromes",
        "Include Aho-Corasick for multiple pattern matching",
        "Use dynamic programming for edit distance variants",
        "Implement with Rabin-Karp rolling hash optimization",
        "Add Boyer-Moore bad character and good suffix heuristics",
        "Use regex compilation for repeated pattern matching",
        "Implement with bit manipulation for character sets",
        "Include string interning for memory efficiency",
        "Use join() instead of concatenation in loops",
        "Implement with generator for memory-efficient processing",
        "Add Unicode normalization for robust comparison",
        "Use collections.Counter for character frequency",
        "Implement with early termination optimization",
    ],
    
    "divide_and_conquer": [
        "Implement with classic divide into equal halves",
        "Use three-way partitioning for better cache locality",
        "Include merge operation with sentinel optimization",
        "Add analysis of recurrence relation (Master theorem)",
        "Implement with iterative bottom-up merging",
        "Use in-place partitioning to reduce space complexity",
        "Include threshold for switching to simpler algorithm",
        "Add median-of-medians for guaranteed good pivots",
        "Implement with parallel divide for large inputs",
        "Use auxiliary space efficiently with buffer reuse",
        "Include detailed complexity analysis at each level",
        "Add visualization of recursion tree structure",
        "Implement with tail recursion optimization",
        "Use iterative stack simulation for deep recursion",
        "Include comparison with naive approach in comments",
        "Add proof of correctness sketch in docstring",
        "Implement with randomization for average case",
        "Use memoization for overlapping subproblems",
        "Include both stable and unstable variants",
        "Add adaptive behavior based on input characteristics",
    ],
    
    "greedy_algorithms": [
        "Implement with priority queue for optimal selection",
        "Use sorting as preprocessing step for greedy choice",
        "Include proof of greedy choice property in comments",
        "Add optimal substructure explanation in docstring",
        "Implement with min/max heap for efficient selection",
        "Use interval scheduling with earliest deadline first",
        "Include counterexample for non-greedy approaches",
        "Add exchange argument proof sketch",
        "Implement with local optimization leading to global",
        "Use stays-ahead proof strategy in comments",
        "Include matroids framework explanation if applicable",
        "Add comparison with dynamic programming solution",
        "Implement with careful tie-breaking rules",
        "Use lazy evaluation for efficiency",
        "Include analysis of approximation ratio if approximate",
        "Add examples showing greedy vs optimal in docstring",
        "Implement with online algorithm variant",
        "Use amortized analysis for data structure operations",
        "Include certification of optimality method",
        "Add visualization of greedy choices sequence",
    ],
    
    "mathematical": [
        "Implement with modular arithmetic for large numbers",
        "Use Sieve of Eratosthenes for prime generation",
        "Include extended Euclidean algorithm for GCD",
        "Add fast exponentiation with binary method",
        "Implement with Miller-Rabin primality testing",
        "Use Chinese Remainder Theorem for modular equations",
        "Include matrix exponentiation for recurrences",
        "Add Fermat's little theorem applications",
        "Implement with number theoretic transform for FFT",
        "Use dynamic programming for combinatorial counting",
        "Include memoization for recursive number theory",
        "Add Wilson's theorem for prime testing",
        "Implement with Pollard's rho algorithm for factorization",
        "Use inclusion-exclusion principle for counting",
        "Include generating functions approach in comments",
        "Add modular multiplicative inverse calculation",
        "Implement with Gaussian elimination for linear systems",
        "Use Strassen algorithm for matrix multiplication",
        "Include BigInteger handling for arbitrary precision",
        "Add numerical stability considerations in comments",
    ],
    
    "stdlib_operations": [
        "Chain multiple operations together",
        "Use generator expressions for memory efficiency",
        "Combine with lambda functions",
        "Use partial application from functools",
        "Leverage built-in functions like map, filter, reduce",
        "Use itertools.groupby for consecutive grouping",
        "Implement with operator module for functional style",
        "Add collections.ChainMap for multiple dict lookup",
        "Use contextlib for resource management",
        "Implement with itertools.chain for lazy concatenation",
        "Add functools.lru_cache for automatic memoization",
        "Use itertools.accumulate for running totals",
        "Implement with collections.namedtuple for readability",
        "Add itertools.product for Cartesian products",
        "Use functools.wraps for decorator preservation",
        "Implement with itertools.combinations or permutations",
        "Add heapq.nlargest or nsmallest for top-k",
        "Use bisect module for maintaining sorted sequences",
        "Implement with collections.OrderedDict for LRU cache",
        "Add itertools.zip_longest for uneven sequences",
        "Use functools.singledispatch for polymorphism",
        "Implement with dataclasses for cleaner code",
        "Add typing module for static type checking",
        "Use itertools.takewhile or dropwhile for filtering",
    ]
}

_DEFAULT_VARIATIONS = [
    "Handle edge cases explicitly (empty input, single element, None)",
    "Optimize for readability over performance",
    "Optimize for performance over readability",
    "Include comprehensive input validation with type checking",
    "Use Pythonic idioms and follow PEP 8 guidelines",
    "Handle empty inputs with appropriate return values",
    "Include detailed type hints for all parameters and returns",
    "Use descriptive variable names following domain conventions",
    "Add defensive programming checks and assertions",
    "Include examples of both typical and edge cases in docstring",
    "Use constants for magic numbers and configuration",
    "Implement with error handling using try-except blocks",
    "Add logging or debug print statements for tracing",
    "Use context managers for resource cleanup",
    "Include unit test examples in docstring",
    "Optimize for maintainability with clear comments",
    "Use design by contract with preconditions/postconditions",
    "Implement with immutable data structures where possible",
    "Add performance benchmarking code in comments",
    "Use property decorators for computed attributes",
]

def _get_variations(category):
    return _VARIATIONS.get(category, _DEFAULT_VARIATIONS)

# === Utility functions ===

def _read_prompt_template():
    if not PROMPT_PATH.exists():
        return "Category:\n{{category}}\n\nRespond with a single JSON object: {\"code\":..., \"complexity\":...}"
    return PROMPT_PATH.read_text()

def _make_prompt(category, subcategory=None, variation_requirement=None):
    template = _read_prompt_template()
    prompt = template.replace("{{category}}", category or "")
    if "{{subcategory}}" in prompt:
        prompt = prompt.replace("{{subcategory}}", subcategory or "")
    else:
        if subcategory:
            prompt += f"\nSubcategory:\n{subcategory}\n"
    if "{{variation_requirement}}" in prompt:
        prompt = prompt.replace("{{variation_requirement}}", variation_requirement or "")
    else:
        if variation_requirement:
            prompt += f"\nAdditional requirement for variation:\n{variation_requirement}\n"
    return prompt

def _call_ollama(prompt, retries=3, backoff=1.0):
    url = "http://host.docker.internal:11434/api/generate" #url = "http://localhost:11434/api/generate"  API endpoint 
    payload = {
        "model": "deepseek-coder-v2",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.2
    }
    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=120)
            if r.status_code == 200:
                data = r.json()
                if "response" in data:
                    return data["response"].strip()
                if "output" in data:
                    return data["output"].strip()
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(backoff * (attempt + 1))
    return f"ERROR: Ollama server did not return a valid response after {retries} attempts."
def _hash_code(code_text):
    return hashlib.sha1(code_text.encode("utf-8")).hexdigest()

def _extract_ast_safe(code):
    try:
        import sys
        import os
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        from parse_ast import extract_ast
    except Exception as e:
        return {"error": f"parse_ast import failed: {e}"}
    try:
        return extract_ast(code)
    except Exception as e:
        return {"error": f"extract_ast failed: {e}"}

# === Dataset utils ===

def _load_existing_hashes():
    seen = set()
    if OUTPUT_PATH.exists():
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if "code" in obj:
                        seen.add(_hash_code(obj["code"]))
                except Exception:
                    pass
    print(f"Loaded {len(seen)} existing samples from {OUTPUT_PATH}")
    return seen

def _save_sample(data):
    with open(OUTPUT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

# === Generation logic ===

def generate_example(category, subcategory=None, variation_requirement=None):
    prompt = _make_prompt(category, subcategory=subcategory, variation_requirement=variation_requirement)
    output = _call_ollama(prompt)
    parsed = None
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        start = output.find("{")
        end = output.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(output[start:end+1])
            except json.JSONDecodeError:
                parsed = None
    if not parsed:
        parsed = {"code": "", "complexity": "unknown", "raw": output}
    if "code" not in parsed:
        parsed["code"] = ""
    parsed["ast"] = _extract_ast_safe(parsed["code"])
    parsed["category"] = category
    if subcategory:
        parsed["subcategory"] = subcategory
    if variation_requirement:
        parsed["variation"] = variation_requirement
    return parsed

def generate_for_category(category, seen, num_samples=100, max_attempts_per_sample=5, delay=0.5):
    written = 0
    attempts = 0
    duplicates_count = 0
    print(f"\n=== Generating for category '{category}' ===")
    subcategories = ComplexityCategory.get(category, {}).get("subcategories", [])
    variations = _get_variations(category)
    while written < num_samples and attempts < num_samples * max_attempts_per_sample:
        if subcategories:
            sub = subcategories[written % len(subcategories)]
        else:
            sub = None
        var_req = variations[written % len(variations)] if variations else None
        data = generate_example(category, subcategory=sub, variation_requirement=var_req)
        code_text = data.get("code", "")
        h = _hash_code(code_text)
        attempts += 1

        if not code_text.strip() and data.get("raw", "").strip() == "":
            print(f"  Skipping empty output (attempt {attempts})")
            time.sleep(delay)
            continue
        
        is_duplicate = h in seen
        if is_duplicate:
            duplicates_count += 1
            print(f"  Duplicate detected (attempt {attempts}), but saving anyway...")

        seen.add(h)
        _save_sample(data)
        written += 1
        progress_extra = []
        if sub:
            progress_extra.append(f"sub={sub}")
        duplicate_marker = " [DUPLICATE]" if is_duplicate else ""
        print(f"  [{written}/{num_samples}] complexity={data.get('complexity', 'unknown')}{duplicate_marker}" + (" (" + ", ".join(progress_extra) + ")" if progress_extra else ""))
        time.sleep(delay)

    if written < num_samples:
        print(f"Finished with {written} samples (stopped after {attempts} attempts).")
        if duplicates_count > 0:
            print(f"  Note: {duplicates_count} duplicates were saved.")
    else:
        print(f"Completed {written} samples for '{category}'.")
        if duplicates_count > 0:
            print(f"  Note: {duplicates_count} duplicates were saved.")

# === Entry point ===

def main():
    parser = argparse.ArgumentParser(description="Generate code+AST samples from DeepSeek by category")
    parser.add_argument("--categories", "-c", required=True,
                        help="Comma-separated list of categories (e.g. 'sorting,regex,io')")
    parser.add_argument("--delay", "-d", type=float, default=0.5,
                        help="Seconds to wait between calls")
    args = parser.parse_args()

    seen = _load_existing_hashes()
    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    for cat in categories:
        if cat not in ComplexityCategory:
            print(f"Warning: Category '{cat}' not found in ComplexityCategory. Skipping.")
            continue
        target_count = ComplexityCategory[cat].get("target_count", 100)
        print(f"Using target_count={target_count} for category '{cat}' (from ComplexityCategory)")
        generate_for_category(cat, seen, num_samples=target_count, delay=args.delay)

if __name__ == "__main__":
    main()
