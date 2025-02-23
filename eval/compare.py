import os
import json
import matplotlib.pyplot as plt
import numpy as np

# 读取 ./eval/result 目录下的所有 JSON 文件
directory = "./eval/result"
output_path = os.path.join(directory, "scores.png")  # 保存路径
data = {}

for filename in os.listdir(directory):
    if filename.endswith(".json"):
        filepath = os.path.join(directory, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
            file_key = os.path.splitext(filename)[0]  # 去掉后缀
            data[file_key] = content

# 提取数据
files = list(data.keys())
metrics = ["avg_faithfulness", "avg_answer_relevancy", "avg_context_precision", "avg_context_recall"]
values = {metric: [data[file].get(metric, 0) for file in files] for metric in metrics}

# 绘制柱状图
x = np.arange(len(files))  # X 轴位置
width = 0.2  # 柱宽

fig, ax = plt.subplots(figsize=(12, 6))

# 依次绘制四个指标
for i, metric in enumerate(metrics):
    ax.bar(x + i * width, values[metric], width, label=metric)

ax.set_xlabel("File Name")
ax.set_ylabel("Value")
ax.set_title("Evaluation Metrics by File")
ax.set_xticks(x + width * 1.5)
ax.set_xticklabels(files, rotation=45, ha="right")
ax.legend()

plt.tight_layout()

# 保存图片
plt.savefig(output_path, dpi=300)
plt.close()

print(f"图表已保存至 {output_path}")
