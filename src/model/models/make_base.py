from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigcode/starcoder2-3b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

model.save_pretrained("models/student/base")
tokenizer.save_pretrained("models/student/base")