import json
from pathlib import Path

DATA_PATH = Path("data/raw/generated.jsonl")
TRAIN_PATH = Path("data/processed/train.jsonl")
TRAIN_PATH.parent.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "r", encoding="utf-8") as f_in, open(TRAIN_PATH, "w", encoding="utf-8") as f_out:
    for line in f_in:
        item = json.loads(line)
        code = item.get("code", "").strip()
        complexity = item.get("complexity", "unknown")
        if not code or complexity == "unknown":
            continue
        # Optional: include AST
        # ast_text = json.dumps(item.get("ast", {}))
        # input_text = f"AST: {ast_text}\nCode:\n{code}"
        input_text = code
        f_out.write(json.dumps({"input": input_text, "output": complexity}) + "\n")
