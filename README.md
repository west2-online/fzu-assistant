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
1. 安装依赖
    ```bash
    pip install -r requirements.txt
    ```

2. 下载模型
    ```bash
    export HF_ENDPOINT="https://hf-mirror.com"
    until huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --local-dir ./models/DeepSeek-R1-Distill-Qwen-7B; do : ; done
    until huggingface-cli download TencentBAC/Conan-embedding-v1 --local-dir ./models/Conan-embedding-v1; do : ; done
    until huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir ./models/Qwen2.5-7B-Instruct; do : ; done
    ```
3. 安装neo4j
    使用docker安装
    ```bash
    docker run -p 7474:7474 -p 7687:7687 -v $PWD/data:/data -v $PWD/plugins:/plugins --name neo4j-apoc -e NEO4J_apoc_export_file_enabled=true -e NEO4J_apoc_import_file_enabled=true -e NEO4J_apoc_import_file_use__neo4j__config=true -e NEO4JLABS_PLUGINS=\[\"apoc\"\] neo4j:latest
    ```
    本地安装
    ```bash
    # neo4j
    ## java env
    sudo apt install openjdk-11-jdk

    ## download
    # curl -O https://dist.neo4j.org/neo4j-community-4.4.41-unix.tar.gz neo4j.tar.gz
    tar -xf neo4j-community-4.4.41-unix.tar.gz
    mv neo4j-community-4.4.41 nj
    sed -i '/#dbms.security.auth_enabled/s/^#//g' nj/conf/neo4j.conf

    ## use apoc
    mv nj/labs/apoc-4.4.0.35-core.jar nj/plugins/
    echo "dbms.security.procedures.unrestricted=apoc.*" >> nj/conf/neo4j.conf
    echo "apoc.import.file.enabled=true" >> nj/conf/neo4j.conf
    echo "apoc.export.file.enabled=true" >> nj/conf/neo4j.conf
    echo "dbms.default_listen_address=0.0.0.0" >> nj/conf/neo4j.conf

    ## 防火墙
    sudo ufw allow 7474
    sudo ufw allow 7687

    ## run
    nj/bin/neo4j start
    ```

# 训练
```bash
python train.py
```
# 知识图谱可视化
![knowledge graph](https://github.com/west2-online/AI_answer/blob/deployment/img/kg.png?raw=true)

# 工作流
![workflow](https://github.com/west2-online/AI_answer/blob/deployment/img/workflow.png?raw=true)

# TODO
- [ ] RAG-Fusion流程构建
- [ ] 评估
- [ ] 知识融合
- [ ] 使用语义层，而非生成直接cypher？
