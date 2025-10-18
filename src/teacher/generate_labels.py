from transformers import AutoModelForCausalLM, AutoTokenizer
import torch, json

model_id = "deepseek-ai/deepseek-coder-v2-instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", load_in_4bit=True)

def label_example(code, ast):
    prompt = f"""You are an expert in algorithmic complexity.
Analyze the following code and AST to predict its time complexity.

CODE:
{code}

AST SUMMARY:
{ast}

Respond in JSON: {{"complexity": "O(...)", "reasoning": "..."}}"""
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_new_tokens=200)
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return text

def label_batch(input_dir, output_dir):
    for file in os.listdir(input_dir):
        data = json.load(open(os.path.join(input_dir, file)))
        label = label_example(data["code"], data["ast"])
        json.dump({"code": data["code"], "ast": data["ast"], "label": label},
                  open(os.path.join(output_dir, file), "w"))
