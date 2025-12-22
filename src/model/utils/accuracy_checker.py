import argparse, requests, time, json, difflib, sys

OUR_URL = "http://127.0.0.1:5000/analyze"
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OUR_OUTPUT = "./our_model_output.txt"
DEEPSEEK_OUTPUT = "./deepseek_output.txt"

PROMPTS = [
    "def find_max(nums): return max(nums)",
    "def print_pairs(nums):\n    for i in nums:\n        for j in nums:\n            print(i, j)",
    "def binary_search(arr, target):\n    low, high = 0, len(arr)-1\n    while low <= high:\n        mid = (low + high)//2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1",
    "def sum_matrix(matrix):\n    total = 0\n    for row in matrix:\n        for val in row:\n            total += val\n    return total",
    "def reverse_string(s):\n    return s[::-1]",
    "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)",
    "def unique_elements(nums):\n    seen = set()\n    for n in nums:\n        seen.add(n)\n    return list(seen)",
    "def sort_then_sum(nums):\n    nums.sort()\n    return sum(nums)",
    "def nested_triple(nums):\n    for i in nums:\n        for j in nums:\n            for k in nums:\n                print(i, j, k)",
    "def find_duplicate(nums):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] == nums[j]:\n                return True\n    return False"
]

def query_our_model(code):
    try:
        r = requests.post(
            OUR_URL,
            json={"code": code},
            timeout=60
        )
        if r.status_code == 200:
            data = r.json()
            return data.get("complexity", "").strip()
        else:
            return f"Error {r.status_code}"
    except Exception as e:
        return f"Error: {e}"

def query_deepseek_ollama(prompt, retries=3, backoff=1.0):
    payload = {
        "model": "deepseek-coder-v2",
        "prompt": (
            "Analyze the following Python function and respond ONLY with its Big-O time complexity and nothing else (e.g. O(n)):\n\n"
            f"{prompt}\n\nComplexity:"
        ),
        "stream": False,
        "temperature": 0.2
    }
    headers = {"Content-Type": "application/json"}

    for attempt in range(retries):
        try:
            r = requests.post(OLLAMA_URL, json=payload, headers=headers, timeout=120)
            if r.status_code == 200:
                data = r.json()
                if "response" in data:
                    return data["response"].strip()
                elif "output" in data:
                    return data["output"].strip()
            else:
                print(f"{r.status_code}")
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
        time.sleep(backoff * (attempt + 1))

    return f"Ollama failed after {retries} retries"

def compare_model_accuracy():
    #Try to read both of the files which is our model's output and DeepSeek output
    try:
        #Read our model's output from file
        with open('our_model_output.txt', 'r', encoding='utf-8') as f:
            our_outputs = [line.strip() for line in f if line.strip()]

        #Read DeepSeek's output from file
        with open('deepseek_output.txt', 'r', encoding='utf-8') as f:
            deepseek_outputs = [line.strip() for line in f if line.strip()]
   
    except FileNotFoundError as e:
        #If file not found, print error message.
        print(f" File Error: {e}")
        print("\n Please make sure both files exist:")
        print(" - our_model_output.txt (our model's output)")
        print(" - deepseek_output.txt (DeepSeek's output)")
        return

    # Compare as many examples as we have in both files
    if len(our_outputs) != len(deepseek_outputs):
        print(f"Warning: Files have different lengths ({len(our_outputs)} vs {len(deepseek_outputs)})")
        min_len = min(len(our_outputs), len(deepseek_outputs))
        our_outputs = our_outputs[:min_len]
        deepseek_outputs = deepseek_outputs[:min_len]
        print(f"Using first {min_len} examples from both files\n")
    else:
        print(f"Comparing {len(our_outputs)} examples from both files\n")

    #Counting the number of examples that we are comparing
    total = len(our_outputs)

    exact_matches = 0
    close_matches = 0
    different_outputs = 0

    #Comparing each example one by one
    for i in range(total):
        our_answer = our_outputs[i]
        deepseek_answer = deepseek_outputs[i]

        #Check for exact match in the answers
        if our_answer == deepseek_answer:
            exact_matches = exact_matches + 1
            print(f"Example {i+1}: Exact Match")
        else:
            # Calculate how similar the answers are (0% to 100%)
            similarity = difflib.SequenceMatcher(None, our_answer, deepseek_answer).ratio()

            # If answers are 80% or more similar, count as "close match"
            if similarity >= 0.8:
                close_matches = close_matches + 1
                print(f"Example {i+1}: Close Match ({similarity:.0%} similar)")
            
            # If answers are less than 80% similar, count as different
            else:
                different_outputs = different_outputs + 1
                print(f"Example {i+1}: Different Outputs ({similarity:.0%} similar)")
                print(f"  Our model: {our_answer[:80]}...")
                print(f"  DeepSeek:  {deepseek_answer[:80]}...")
    
    #Calculating the accuracy percentages
    exact_accuracy = (exact_matches / total) * 100
    close_accuracy = ((close_matches + exact_matches) / total) * 100

   
    #Displaying the final results
    print()
    print("=" * 50)
    print("ACCURACY RESULTS")
    print("=" * 50)
    print(f"Total examples compared: {total}")
    print()
    print(f"Exact matches: {exact_matches} ({exact_accuracy:.1f}%)")
    print(f"Close matches: {close_matches} ({close_accuracy:.1f}%)")
    print(f"Different: {different_outputs}")
    print()
    print(f"EXACT ACCURACY: {exact_accuracy:.1f}%")
    print(f"CLOSE+EXACT ACCURACY: {close_accuracy:.1f}%")
    print()

    
    # Give a simple rating and accuracy based on how accurate our model is
    if exact_accuracy >= 90:
        rating = f"Excellent ({exact_accuracy:.1f}%)"
    elif exact_accuracy >= 80:
        rating = f"Good ({exact_accuracy:.1f}%)"
    elif exact_accuracy >= 70:
        rating = f"Fair ({exact_accuracy:.1f}%)"
    else:
        rating = f"Needs Improvement ({exact_accuracy:.1f}%)"
    
    print(f"Overall Rating: {rating}")
    print("=" * 50)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run model accuracy comparison.")
    parser.add_argument("--ours", type=str, default="true", help="Run our model (true/false)")
    parser.add_argument("--deepseek", type=str, default="true", help="Run DeepSeek (true/false)")
    parser.add_argument("--compare-only", type=str, default="false", help="Only compare existing files")

    args = parser.parse_args()
    ours_flag = args.ours.lower() == "true"
    deepseek_flag = args.deepseek.lower() == "true"
    compare_only = args.compare_only.lower() == "true"

    if compare_only:
        print("Comparison only\n")
        compare_model_accuracy()
        sys.exit(0)

    print(f"\n[CONFIG] ours={ours_flag}, deepseek={deepseek_flag}\n")

    if ours_flag:
        with open(OUR_OUTPUT, "w", encoding="utf-8") as f_ours:
            for i, code in enumerate(PROMPTS, 1):
                print(f"[{i}/{len(PROMPTS)}] CPA Running")
                ours = query_our_model(code)
                print(f" → {ours}\n")
                f_ours.write(ours + "\n")

    if deepseek_flag:
        with open(DEEPSEEK_OUTPUT, "w", encoding="utf-8") as f_deep:
            for i, code in enumerate(PROMPTS, 1):
                print(f"[{i}/{len(PROMPTS)}] DeepSeek Running")
                deep = query_deepseek_ollama(code)
                print(f" → {deep}\n")
                f_deep.write(deep + "\n")

    print("\nDone\n")
    compare_model_accuracy()