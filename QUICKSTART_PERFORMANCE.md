# Quick Start: Performance Testing

## 5-Minute Guide to Automated Performance Testing

### Prerequisites
- Docker Desktop running (or Python 3.x with CUDA GPU)
- VS Code with the extension installed
- The model server running

### Step 1: Start the Server (if not already running)

```bash
# Inside Docker container
cd /app/src/model
nohup python serve.py > server.log 2>&1 &
```

Wait for: `"Server running at http://0.0.0.0:5000"` in the logs.

### Step 2: Test in VS Code

1. **Open a Python file** or create a new one:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
```

2. **Select the entire function**

3. **Right-click** → Choose **"CPA: Analyze & Generate Performance Test"**

4. **Wait** (~10-30 seconds for analysis and generation)

5. **Save the test file** that opens (e.g., `bubble_sort_performance_test.py`)

### Step 3: Run the Test

```bash
# Install dependencies (first time only)
pip install matplotlib numpy

# Run the test
python bubble_sort_performance_test.py
```

### Expected Output

```
==================================================================
Performance Testing: bubble_sort
Predicted Complexity: O(n²)
==================================================================

Testing with input size: 10... Time: 0.0234ms, Memory: 12.50KB
Testing with input size: 50... Time: 0.5123ms, Memory: 14.25KB
Testing with input size: 100... Time: 2.1456ms, Memory: 18.75KB
...

Complexity Analysis: Empirical: O(n²) (predicted: O(n²))

Plot saved to: bubble_sort_performance.png
```

### Step 4: View Results

1. **Check the console** for detailed timing data
2. **Open the PNG file** to see performance graphs
3. **Compare** empirical vs. predicted complexity

## Try These Examples

### Example 1: Linear Search (O(n))

```python
def linear_search(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
```

### Example 2: Binary Search (O(log n))

```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1
```

### Example 3: Merge Sort (O(n log n))

```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

## Command-Line Alternative

If you prefer command-line:

```bash
# Using PowerShell
$body = @{ code = "def loop(n):`n    for i in range(n): pass" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:5000/generate-test" -Method POST -Body $body -ContentType "application/json" | Select-Object -ExpandProperty Content
```

Save the returned `test_file` content and run it!

## Tips

- **Start small**: Test with simple functions first
- **Check predictions**: Compare model predictions with actual results
- **Adjust test sizes**: Edit generated files to use different input sizes
- **Watch resources**: Some algorithms need more memory/time

## Next Steps

- Read [PERFORMANCE_TESTING.md](PERFORMANCE_TESTING.md) for detailed documentation
- Try the example functions in `src/model/examples/example_functions.py`
- Customize generated tests for your specific needs
- Set up automated performance regression testing

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Server not responding | Check `tail -f server.log` for errors |
| Import errors in test | Run `pip install matplotlib numpy` |
| Tests too slow | Reduce test sizes in generated file |
| No function detected | Select complete function including `def` |

---

**Ready to optimize your code! 🚀**

