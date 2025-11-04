#!/usr/bin/env python3
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import sys

MODEL_PATH = "./models/student/tuned"

print("Loading model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0,        # GPU
)

if len(sys.argv) > 1:
    code_snippet = sys.argv[1]

else:
    print("Default prompt")
    code_snippet = "nums = [1, 0, 1, 5, 7]\n nums.sort()\n print(nums)\n"

prompt = f"### Input:\n{code_snippet}\n\n### Output:\n"

output = generator(
    prompt,
    max_new_tokens=10,
    do_sample=False,
)

generated = output[0]["generated_text"]
answer = generated.split("### Output:")[-1].strip().split("\n")[0]

print("Output (Everything below this line is the model's output):")
print(answer)
