import subprocess, json, os, random, time
from pathlib import Path
from parse_ast import extract_ast

PROMPT_PATH = Path("data/prompts/prompt.txt")
OUTPUT_PATH = Path("data/raw/generated.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Some toy seed snippets for DeepSeek to expand on
SEED_SNIPPETS = [
    "def bubble_sort(arr):\n    for i in range(len(arr)):\n        for j in range(0, len(arr)-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]",
    "def binary_search(arr, x):\n    l, r = 0, len(arr)-1\n    while l <= r:\n        mid = (l+r)//2\n        if arr[mid] == x: return mid\n        elif arr[mid] < x: l = mid + 1\n        else: r = mid - 1",
    "def count_pairs(nums):\n    s = 0\n    for i in nums:\n        for j in nums:\n            if i < j: s += 1\n    return s",
]

def generate_example(code_snippet):
    with open(PROMPT_PATH) as f:
        prompt = f.read().replace("{{code}}", code_snippet)

    # Call DeepSeek via Ollama
    cmd = ["ollama", "run", "deepseek-coder-v2", prompt]
    result = subprocess.run(cmd, capture_output=True, text=True)

    output = result.stdout.strip()
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        data = {"code": code_snippet, "complexity": output}

    data["ast"] = extract_ast(code_snippet)
    return data


def main(num_samples=10000):
    with open(OUTPUT_PATH, "a") as f:
        for i in range(num_samples):
            code = random.choice(SEED_SNIPPETS)
            data = generate_example(code)
            f.write(json.dumps(data) + "\n")
            print(f"[{i+1}/{num_samples}] {data['complexity']}")
            time.sleep(0.5)


if __name__ == "__main__":
    main()
