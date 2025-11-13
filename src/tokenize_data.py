
#!/usr/bin/env python3
from datasets import load_dataset
from transformers import AutoTokenizer

# Directories
MODEL_NAME = "./models/student/base"
DATA_PATH = "./data/processed/train.jsonl"
OUTPUT_PATH = "./data/tokenized"


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token


print(f"Loading dataset from {DATA_PATH} ...")
dataset = load_dataset("json", data_files=DATA_PATH, split="train")


def format_example(example):
    return {"text": f"### Input:\n{example['input']}\n\n### Output:\n{example['output']}"}

dataset = dataset.map(format_example)

def tokenize(example):
    return tokenizer(
        example["text"],
        truncation=True,
        padding="max_length",
        max_length=256,   # Tweak depending on training data length and gpu memory
    )

print("Tokenizing")
tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)


tokenized_dataset.save_to_disk(OUTPUT_PATH)
print(f"✅ Tokenized data saved to {OUTPUT_PATH}")
