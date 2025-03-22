#!/bin/bash

# 设置HuggingFace镜像源
export HF_ENDPOINT="https://hf-mirror.com"

# 下载模型
# until huggingface-cli download Qwen/Qwen2.5-14B-Instruct-1M --local-dir ./models/Qwen2.5-14B-Instruct-1M; do : ; done
modelscope download --model qwen/QWQ-32B-AWQ --local_dir ./models/QWQ-32B-AWQ
until huggingface-cli download Alibaba-NLP/gte-Qwen2-1.5B-instruct --local-dir ./models/gte-Qwen2-1.5B-instruct; do : ; done
# 提取脚本
python3.12 extract_ct.py

# 启动vLLM服务
# VLLM_CONFIGURE_LOGGING=0 \
# vllm serve ./models/Qwen2.5-14B-Instruct-1M \
#     --chat-template ./models/Qwen2.5-14B-Instruct-1M/ct.jinja \
#     --tensor-parallel-size 2 \
#     --gpu-memory-utilization 0.9 \
#     --enforce_eager \
#     --served-model-name chat_llm\
#     --port 8000 &
VLLM_CONFIGURE_LOGGING=0 \
vllm serve ./models/QWQ-32B-AWQ \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.8 \
    --enforce_eager \
    --served-model-name chat_llm\
    --port 8000 &
# VLLM_CONFIGURE_LOGGING=0 \
# vllm serve ./models/Conan-embedding-v1 \
#     --tensor-parallel-size 2\
#     --gpu-memory-utilization 0.1\
#     --enforce_eager\
#     --served-model-name embeddings \
#     --port 8001 &
VLLM_CONFIGURE_LOGGING=0 \
vllm serve ./models/gte-Qwen2-1.5B-instruct \
    --tensor-parallel-size 2\
    --gpu-memory-utilization 0.1\
    --enforce_eager\
    --served-model-name embeddings \
    --port 8001 &
    
# 等待服务启动
sleep 15

# 运行向量数据库
python3.12 vector_store.py

# 运行RAG主程序
python3.12 NaiveRAG.py