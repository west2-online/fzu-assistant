# 技术栈
- 应用框架: langchain，langgraph
- 向量存储: faiss
- 知识图谱存储: neo4j
- 大模型: 
  - [deepseek-ai/DeepSeek-R1-Distill-Qwen-7B](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B)
  - [Qwen/Qwen2.5-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- 嵌入模型: [TencentBAC/Conan-embedding-v1](https://huggingface.co/TencentBAC/Conan-embedding-v1)
- RAG, GraphRAG, RAG-Fusion

# 环境配置
[开发文档](https://github.com/west2-online/AI_answer/blob/deployment/docs/develop.md)

# 知识图谱可视化
![knowledge graph](https://github.com/west2-online/AI_answer/blob/deployment/img/kg.png?raw=true)

# 工作流
![workflow](https://github.com/west2-online/AI_answer/blob/deployment/img/workflow.png?raw=true)

# TODO
- [ ] 评估
- [ ] 知识融合
- [ ] 使用语义层，而非生成直接cypher？
- [ ] 服务端
- [ ] 追踪token使用量
