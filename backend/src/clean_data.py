import json
from pathlib import Path

RAW = Path("data/raw/generated.jsonl")
CLEAN = Path("data/processed/clean.jsonl")

def is_valid(entry):
    c = entry.get("complexity", "")
    return c.startswith("O(") and len(c) < 20

def main():
    with open(RAW) as f, open(CLEAN, "w") as out:
        for line in f:
            try:
                entry = json.loads(line)
                if is_valid(entry):
                    out.write(json.dumps(entry) + "\n")
            except json.JSONDecodeError:
                continue

if __name__ == "__main__":
    main()
