#!/usr/bin/env python3
import torch
from flask import Flask, request, jsonify
from transformers import AutoTokenizer, AutoModelForCausalLM
from performance_test_generator import PerformanceTestGenerator

MODEL_PATH = "./models/student/cpa"
MAX_INPUT_LENGTH = 512  # prevent too-long inputs

# Load model & tokenizer
print("Loading model")
print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=torch.float16)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
torch.backends.cudnn.benchmark = True
model.to(device)
model.eval()
model = torch.compile(model)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

warmup = tokenizer("warmup", return_tensors="pt", padding=True)
warmup = {k: v.to(device) for k, v in warmup.items()}
with torch.inference_mode():
    _ = model.generate(
        warmup["input_ids"],
        attention_mask=warmup["attention_mask"],
        max_new_tokens=1,
        do_sample=False,
        use_cache=True,
        pad_token_id=tokenizer.eos_token_id,
        eos_token_id=tokenizer.eos_token_id
    )

app = Flask(__name__)

# Initialize performance test generator
test_generator = PerformanceTestGenerator()

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    code_snippet = data.get("code", "").strip()
    if not code_snippet:
        return jsonify({"error": "Missing 'code' field"}), 400

    prompt = f"Analyze the following Python function and respond ONLY with its Big-O time complexity:\n\n{code_snippet}\nComplexity:"

    try:
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_LENGTH,
            padding=True
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=16,
                do_sample=False,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )

        decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        complexity = decoded[len(prompt):].strip().split("\n")[0]

        return jsonify({"complexity": complexity})

    except Exception as e:
        print(f"[ERROR] {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/generate-test", methods=["POST"])
def generate_test():
    """
    Generate a performance test file for the provided code.
    
    Expected JSON payload:
    {
        "code": "def my_func(n): ...",
        "complexity": "O(n)"  # Optional - will analyze if not provided
    }
    
    Returns:
    {
        "test_file": "...",  # Generated test file content
        "complexity": "O(n)",  # Complexity used for test generation
        "function_name": "my_func"
    }
    """
    data = request.get_json(force=True)
    code_snippet = data.get("code", "").strip()
    complexity_hint = data.get("complexity", "").strip()
    
    if not code_snippet:
        return jsonify({"error": "Missing 'code' field"}), 400
    
    try:
        # If no complexity provided, analyze it first
        if not complexity_hint:
            prompt = f"Analyze the following Python function and respond ONLY with its Big-O time complexity:\n\n{code_snippet}\nComplexity:"
            
            inputs = tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=MAX_INPUT_LENGTH,
                padding=True
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.inference_mode():
                output_ids = model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_new_tokens=16,
                    do_sample=False,
                    use_cache=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            decoded = tokenizer.decode(output_ids[0], skip_special_tokens=True)
            complexity_hint = decoded[len(prompt):].strip().split("\n")[0]
        
        # Generate test file
        test_file_content = test_generator.generate_test_file(code_snippet, complexity_hint)
        
        if not test_file_content:
            return jsonify({"error": "Failed to generate test file. Make sure code contains a valid function definition."}), 400
        
        # Extract function name for response
        func_info = test_generator.extract_function_info(code_snippet)
        function_name = func_info['name'] if func_info else "unknown"
        
        return jsonify({
            "test_file": test_file_content,
            "complexity": complexity_hint,
            "function_name": function_name,
            "message": f"Performance test generated for {function_name} with complexity {complexity_hint}"
        })
    
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Server running at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
