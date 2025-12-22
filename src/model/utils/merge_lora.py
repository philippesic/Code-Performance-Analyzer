#!/usr/bin/env python3
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

# Directories
BASE_MODEL = "./models/student/base"
LORA_ADAPTERS = "./models/student/adapters"
OUTPUT_MODEL = "./models/student/tuned"

model = AutoModelForCausalLM.from_pretrained(BASE_MODEL)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = PeftModel.from_pretrained(model, LORA_ADAPTERS)

print("Merging adapters")
model = model.merge_and_unload()

os.makedirs(OUTPUT_MODEL, exist_ok=True)
model.save_pretrained(OUTPUT_MODEL)
tokenizer.save_pretrained(OUTPUT_MODEL)
print(f"Merged model saved to {OUTPUT_MODEL}")
