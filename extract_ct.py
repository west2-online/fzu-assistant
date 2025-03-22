import json

def extract_ct(model_path = "./models/Qwen2.5-14B-Instruct-1M"):
    with open(f"{model_path}/tokenizer_config.json", "r") as f:
        ct = json.load(f).get("chat_template")
        print(ct)
    if ct is not None:
        with open(f"{model_path}/ct.jinja", "w") as f:
            f.write(str(ct))

if __name__ == "__main__":
    extract_ct()