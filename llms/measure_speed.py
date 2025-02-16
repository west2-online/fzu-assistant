import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# 设置模型和tokenizer
model_name = "./models/Qwen2.5-7B-Instruct-1M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")

# 输入文本
input_text = "你觉得人生是什么?"  # 替换为你的输入
input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(model.device)

# 预热
max_new_tokens = 4096  # 设定最大生成token数
model.generate(input_ids, max_new_tokens=max_new_tokens)

# 生成输出并计时
start_time = time.perf_counter()

with torch.no_grad():
    output_ids = model.generate(input_ids, max_new_tokens=max_new_tokens)

end_time = time.perf_counter()

# 计算生成的token数和token/s
num_generated_tokens = output_ids.shape[1] - input_ids.shape[1]
elapsed_time = end_time - start_time
tokens_per_second = num_generated_tokens / elapsed_time

print(f"Generated {num_generated_tokens} tokens in {elapsed_time:.2f} seconds.")
print(f"Tokens per second: {tokens_per_second:.2f} token/s")
