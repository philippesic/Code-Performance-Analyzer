#!/usr/bin/env python3
import torch
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "./models/student/cpa"
MAX_INPUT_LENGTH = 512  # prevent too-long inputs

# Load model & tokenizer
print("Loading model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    code_snippet = data.get("code", "").strip()
    if not code_snippet:
        return jsonify({"error": "Missing 'code' field"}), 400

    # Minimal prompt just for complexity analysis
    prompt = f"Analyze the following Python function and respond ONLY with its Big-O time complexity:\n\n{code_snippet}\nComplexity:"

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_LENGTH
        ).to(device)

        max_length = inputs["input_ids"].shape[1] + 16

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=16,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)

        complexity = decoded[len(prompt):].strip().split("\n")[0]

        return jsonify({"complexity": complexity})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Server running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
