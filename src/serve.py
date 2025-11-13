#!/usr/bin/env python3
import torch
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "./models/student/tuned"

print("Loading model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    code_snippet = data.get("code", "").strip()
    if not code_snippet:
        return jsonify({"error": "Missing 'code' field"}), 400

    prompt = f"### Input:\n{code_snippet}\n\n### Output:\n"
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    try:
        with torch.no_grad():
            input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
            max_length = input_ids.shape[1] + 20
            output_ids = model.generate(
                input_ids,
                max_length=max_length,
                do_sample=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )


        text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        answer = text.split("### Output:")[-1].strip().split("\n")[0]

        return jsonify({"complexity": answer})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("starting server at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
