#!/usr/bin/env python3
import torch
from datasets import load_dataset, load_from_disk
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model
import os

# Directories
MODEL_NAME = "./models/student/base"
DATA_PATH = "./dataprocessed/train.jsonl"
TOKENIZED_PATH = "./data/tokenized/"
OUTPUT_DIR = "./models/student/adapters"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

if os.path.exists(TOKENIZED_PATH):
    print(f"Loading data from {TOKENIZED_PATH}")
    tokenized_dataset = load_from_disk(TOKENIZED_PATH)
else:
    dataset = load_dataset("json", data_files=DATA_PATH, split="train")

    def format_example(example):
        return {"text": f"### Input:\n{example['input']}\n\n### Output:\n{example['output']}"}

    dataset = dataset.map(format_example)

    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            padding="max_length",
            max_length=512,
        )

    tokenized_dataset = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)
    tokenized_dataset.save_to_disk(TOKENIZED_PATH)
    print(f"Saved tokenized data to {TOKENIZED_PATH}")

# 4b conf
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

print("Loading base model")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
)

# LoRA configs
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)

data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)

# Arg
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=2, # Tweak per gpu
    gradient_accumulation_steps=2, # Tweak per gpu
    num_train_epochs=3, # Tweak per gpu
    learning_rate=5e-5,
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    save_total_limit=2,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

print("Training")
print("Init gpu memory", round(torch.cuda.memory_allocated()/1e9, 2), "gb")

trainer.train()

model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Adapters saved to {OUTPUT_DIR}")
