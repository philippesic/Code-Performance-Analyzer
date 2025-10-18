import json, os

def build_training_data(labeled_dir, out_path):
    samples = []
    for f in os.listdir(labeled_dir):
        d = json.load(open(os.path.join(labeled_dir, f)))
        samples.append({
            "instruction": "Estimate time complexity (Big-O).",
            "input": d["code"] + "\n\nAST SUMMARY:\n" + d["ast"],
            "output": d["label"]["complexity"]
        })
    json.dump(samples, open(out_path, "w"))
