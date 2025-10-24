from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_dataset

MODEL_NAME = "models/student/base"  # your local HF model path
DATA_PATH = "data/processed/train.jsonl"

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Add pad token if missing
if tokenizer.pad_token is None:
    tokenizer.add_special_tokens({'pad_token': tokenizer.eos_token})

# Load model
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Resize embeddings if new token was added
model.resize_token_embeddings(len(tokenizer))

# Load dataset
dataset = load_dataset("json", data_files={"train": DATA_PATH})

# Tokenize function
def tokenize_fn(batch):
    enc = tokenizer(batch["input"], truncation=True, padding="max_length", max_length=512)
    enc["labels"] = enc["input_ids"].copy()  # use input_ids as labels for causal LM
    return enc


# Tokenize dataset
tokenized_dataset = dataset["train"].map(tokenize_fn, batched=True)

# Training arguments
training_args = TrainingArguments(
    output_dir="models/student/tuned",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    learning_rate=5e-5,
    save_strategy="epoch",
    logging_steps=10,
    fp16=True,  # enable if you have GPU
    push_to_hub=False
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    tokenizer=tokenizer
)


trainer.train()
trainer.save_model("models/student/tuned")
