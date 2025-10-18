import requests, json, os

TEACHER_MODEL = "deepseek-coder-v2:7b"

def get_complexity(code: str) -> str:
    prompt = f"""Analyze the following function and provide its time complexity in Big-O notation.

Code:
{code}

Respond only with the Big-O expression (e.g. O(n log n), O(1), O(n^2)).
"""
    resp = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": TEACHER_MODEL, "prompt": prompt, "stream": False}
    )
    data = resp.json()
    return data["response"].strip()

if __name__ == "__main__":
    example_code = """
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""
    print("Predicted Complexity:", get_complexity(example_code))
