# Usage Instructions:
# ollama serve
# python src/generte_data.py --categories <category> --num <num> --delay <sec>


import subprocess, json, os, random, time, argparse, hashlib, requests
from pathlib import Path

# === Paths ===
PROMPT_PATH = Path("data/prompts/prompt.txt")
OUTPUT_PATH = Path("data/raw/generated.jsonl")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# === Utility functions ===

def _read_prompt_template():
    if not PROMPT_PATH.exists():
        return "Category:\n{{category}}\n\nRespond with a single JSON object: {\"code\":..., \"complexity\":...}"
    return PROMPT_PATH.read_text()

def _make_prompt(category):
    template = _read_prompt_template()
    return template.replace("{{category}}", category or "")

def _call_ollama(prompt, retries=3, backoff=1.0):
    url = "http://host.docker.internal:11434/api/generate"  #  API endpoint
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

def generate_example(category):
    prompt = _make_prompt(category)
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
    return parsed

def generate_for_category(category, seen, num_samples=100, max_attempts_per_sample=5, delay=0.5):
    written = 0
    attempts = 0
    print(f"\n=== Generating for category '{category}' ===")
    while written < num_samples and attempts < num_samples * max_attempts_per_sample:
        data = generate_example(category)
        code_text = data.get("code", "")
        h = _hash_code(code_text)
        attempts += 1

        if not code_text.strip() and data.get("raw", "").strip() == "":
            print(f"  Skipping empty output (attempt {attempts})")
            time.sleep(delay)
            continue
        if h in seen:
            print(f"  Duplicate (attempt {attempts})")
            time.sleep(delay)
            continue

        seen.add(h)
        _save_sample(data)
        written += 1
        print(f"  [{written}/{num_samples}] complexity={data.get('complexity', 'unknown')}")
        time.sleep(delay)

    if written < num_samples:
        print(f"Finished with {written} samples (stopped after {attempts} attempts).")
    else:
        print(f"Completed {written} samples for '{category}'.")

# === Entry point ===

def main():
    parser = argparse.ArgumentParser(description="Generate code+AST samples from DeepSeek by category")
    parser.add_argument("--categories", "-c", required=True,
                        help="Comma-separated list of categories (e.g. 'sorting,regex,io')")
    parser.add_argument("--num", "-n", type=int, default=100,
                        help="Number of samples per category")
    parser.add_argument("--delay", "-d", type=float, default=0.5,
                        help="Seconds to wait between calls")
    args = parser.parse_args()

    seen = _load_existing_hashes()
    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    for cat in categories:
        generate_for_category(cat, seen, num_samples=args.num, delay=args.delay)

if __name__ == "__main__":
    main()
