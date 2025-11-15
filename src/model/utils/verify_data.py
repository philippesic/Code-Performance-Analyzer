import json
from pathlib import Path
from collections import Counter

DATA_PATH = Path("data/raw/generated.jsonl")

def main():
    if not DATA_PATH.exists():
        print(f"No dataset found at {DATA_PATH}")
        return

    seen_hashes = set()
    duplicates = 0
    missing_fields = 0
    complexity_counter = Counter()
    total = 0

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        for line in f:
            total += 1
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                print(f"Line {total} is invalid JSON")
                continue

            code = item.get("code", "").strip()
            complexity = item.get("complexity", "unknown")
            ast = item.get("ast", None)

            if not code or complexity == "unknown" or not ast:
                missing_fields += 1

            # Hash to check duplicates
            h = hash(code)
            if h in seen_hashes:
                duplicates += 1
            else:
                seen_hashes.add(h)

            complexity_counter[complexity] += 1

    print(f"Total samples: {total}")
    print(f"Duplicates: {duplicates}")
    print(f"Missing fields: {missing_fields}")
    print("Complexity label distribution:")
    for k, v in complexity_counter.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
