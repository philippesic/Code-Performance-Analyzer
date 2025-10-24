#!/usr/bin/env python3
import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_PATH = "models/student/tuned"  # path to tuned model

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
tokenizer.pad_token = tokenizer.eos_token

# Use FP16 if CUDA is available for speed
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32

model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, torch_dtype=dtype)
model.to(device)
model.eval()
print(f"Using device: {device}, dtype: {dtype}")

def get_complexity(snippets, max_length=128):
    """
    Accepts a single code snippet (str) or a list of snippets.
    Returns predicted complexity (str) or list of predictions.
    """
    if isinstance(snippets, str):
        snippets = [snippets]

    prompts = [
        f"Analyze the following Python function and respond ONLY with its Big-O time complexity.\n\n{code}\nComplexity:"
        for code in snippets
    ]

    # Tokenize batch
    inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True, max_length=max_length).to(device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=32,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )

    results = []
    for i, prompt in enumerate(prompts):
        decoded = tokenizer.decode(outputs[i], skip_special_tokens=True)
        answer = decoded[len(prompt):].splitlines()[0].strip()
        results.append(answer)

    return results if len(results) > 1 else results[0]

def main():
    parser = argparse.ArgumentParser(description="Query model for code complexity")
    parser.add_argument("code", type=str, help="Python code snippet (wrap in quotes)")
    args = parser.parse_args()

    complexity = get_complexity(args.code)
    print("Predicted Complexity:", complexity)

if __name__ == "__main__":
    main()
