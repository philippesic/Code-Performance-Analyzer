from transformers import AutoModelForCausalLM, AutoTokenizer

def predict_complexity(code):
    prompt = f"Analyze the following function and output its time complexity:\n\n{code}\n\nAnswer in O(...) form only."
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=50)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
