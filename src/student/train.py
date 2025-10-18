from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

model_id = "bigcode/starcoder2-7b"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", load_in_4bit=True)

peft_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj","v_proj"])
model = get_peft_model(model, peft_config)

# Load your dataset
from datasets import load_dataset
dataset = load_dataset("json", data_files={"train": "data/train/data.json"})

training_args = TrainingArguments(
    output_dir="models/student",
    per_device_train_batch_size=1,
    num_train_epochs=3,
    fp16=True,
    learning_rate=2e-4
)

trainer = Trainer(model=model, args=training_args, train_dataset=dataset["train"])
trainer.train()
