# 开发文档

# 环境配置

三个部分：

1. python包
2. neo4j
3. 模型

## python包

python 版本为3.12

```bash
pip install -r requirements.txt
```

## neo4j

neo4j为可选项，如果要运行现在的graph，还需要运行如下脚本。注意使用curl下载neo4j的那一步骤可能会失败，所以可以提前下载好，在执行后续步骤。

下载地址：[https://dist.neo4j.org/neo4j-community-4.4.41-unix.tar.gz](https://dist.neo4j.org/neo4j-community-4.4.41-unix.tar.gz)

运行完成后，使用浏览器访问：http://ip:7474

### docker

```bash
docker run -p 7474:7474 -p 7687:7687 -v $PWD/data:/data -v $PWD/plugins:/plugins --name neo4j-apoc -e NEO4J_apoc_export_file_enabled=true -e NEO4J_apoc_import_file_enabled=true -e NEO4J_apoc_import_file_use__neo4j__config=true -e NEO4JLABS_PLUGINS=\[\"apoc\"\] neo4j:latest
```

### 本地安装

```bash
# neo4j
## java env
sudo apt install openjdk-11-jdk

## download
curl -O https://dist.neo4j.org/neo4j-community-4.4.41-unix.tar.gz
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

## 模型

### 下载LLM模型和embedding模型：

下载的两个模型如下，如果太大了可以先下一个1.5B的小模型

1. Qwen/Qwen2.5-7B-Instruct-1M
2. TencentBAC/Conan-embedding-v1

```bash
export HF_ENDPOINT="https://hf-mirror.com"
until huggingface-cli download Qwen/Qwen2.5-7B-Instruct-1M --local-dir ./models/Qwen2.5-7B-Instruct-1M; do : ; done
until huggingface-cli download TencentBAC/Conan-embedding-v1 --local-dir ./models/Conan-embedding-v1; do : ; done
```

### 使用vllm进行模型部署LLM模型

1. **！请注意**：第三行- -chat template这里，如果不配置好，模型必然出现错误。需要从huggingface下载的模型的tokenizer_config.json里面找到chat_template字段，保存在jinja文件中
2. 有很多参数可以设置，例如gpu资源需要手动分配等等。参考官方文档。
3. 类似R1系列的推理模型需要配置更多参数
4. 模型部署的更多知识：[https://techcommunity.microsoft.com/blog/machinelearningblog/fundamental-of-deploying-large-language-model-inference/4096881](https://techcommunity.microsoft.com/blog/machinelearningblog/fundamental-of-deploying-large-language-model-inference/4096881)

```bash
# Qwen2.5-7B-Instruct-1M
VLLM_CONFIGURE_LOGGING=0 \
vllm serve ./models/Qwen2.5-7B-Instruct-1M \
    --chat-template ./models/Qwen2.5-7B-Instruct-1M/cj.jinja \
    --tensor-parallel-size 2\
    --gpu-memory-utilization 0.9\
    --port 8000
# DeepSeek-R1-Distill-Qwen-1.5B
VLLM_CONFIGURE_LOGGING=0 \
vllm serve ./models/DeepSeek-R1-Distill-Qwen-1.5B \
    --chat-template ./models/DeepSeek-R1-Distill-Qwen-1.5B/ct.jinja \
    --enable-reasoning \
     --reasoning-parser deepseek_r1\
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.8 \
    --port 8000
```

运行如下脚本，和模型进行命令行交互

```bash
python llms/vllm_llm.py
```

# 关键抽象接口

大致有几个东西

1. config
2. llms
3. embeddings
4. dataloader
5. vector_store
6. graph_store

## 配置项

config.py

目前配置为：

```json
{
    "chat_llm": "./models/Qwen2.5-7B-Instruct-1M",
    "tool_llm": "./models/Qwen2.5-7B-Instruct-1M",
    "embedding_model": "./models/Conan-embedding-v1",
    "neo4j": {
      "url": "bolt://localhost:7687",
      "username": "neo4j",
      "password": "neo4j",
      "database": "neo4j"
    },
    "data_dir": {
        "notice": "./data/notice",
        "QA": "./data/QA",
        "whole": "./data"
    },
    "storage_dir": {
        "vector": "./storage/vector",
        "graph": "./storage/graph"
    },
    "top_k": 20,
    "lightrag_query_mode": "mix"
}
```

使用方法，如果我想取出neo4j的url，有两种方式

```python
from config import conf

print(conf.neo4j.url)
print(conf["neo4j"]["url"])
```

## 大模型

huggingface的版本可以弃了，使用了vllm的openai接口。但是发现vllm是有变化的langchain的VLLM没有办法跟上版本了，所以重新写了一个。

使用方面：自定义langchain的LLM，所以和langchain的LLM一样的，invoke或者stream

最开始使用可以使用命令行交互（必须先运行vllm）：

```python
python llms/vllm_llm.py
```

## 嵌入模型

一般不需要人来使用，都是作为参数传入。

```python
from embeddings import embeddings
```

## 加载数据

使用方法如下，就是将文件夹中的所有文件转成langchain的Document对象

```python
from utils import DataLoader

loader = DataLoader(data_dir=conf.data_dir.whole)
documents = loader.load_and_split()
```

## 向量检索

vector_store.py

可以聚焦于这两个个方法

1. train(documents: t.List[Document], batch=1000):
2. query(question: str) -> t.List[Document]：输入问题字符串，返回相关文档的列表

```python
from embeddings import embeddings
from config import conf
from vector_store import VectorStore

vector_store = VectorStore(embeddings=embeddings, storage_dir=conf.storage_dir.vector)

document_1 = Document(page_content="foo", metadata={"baz": "bar"})
document_2 = Document(page_content="thud", metadata={"bar": "baz"})
document_3 = Document(page_content="i will be deleted :(")
documents = [document_1, document_2, document_3]

vector_store.train(documents=documents)
print(vector_store.query("我要被开了"))
```

## 知识图谱检索

和向量检索同样

1. train(documents: t.List[Document], batch=20):
2. query(question: str) -> t.List[t.Dict]：输入问题，返回和向量检索不一样，返回的是图谱结构信息

```python
from llms import tool_llm
from config import conf
from graph_store import GraphStore

graph_store = GraphStore(llm=tool_llm, 
                         url=conf.neo4j.url,
                         username=conf.neo4j.username,
                         password=conf.neo4j.password)
documents = [Document(page_content="福州大学的校训是“明德至诚，博学远志”")]
graph_store.train(documents)
print(vector_store.query("福州大学的校训是什么？"))
```

# 其他抽象接口

之前没有使用更复杂的算法机制，比如Decomposition，step-back，self-rag等等。因为推理速度奇慢，一个简单问题需要30-60秒的等待时间（很抽象），但是在配置好了vllm后，在同一个问题上有了十几倍的加速比，应该可以尝试很多。

## RAG-Fusion相关

可以先直接运行RAGFusion.py文件

```bash
python RAGFusion.py
```
主要函数的实现：
1. 相关问题生成
2. 倒数重排算法

```python
from utils import QueryGenerator, reciprocal_rank_fusion
from llms import chat_llm, tool_llm

query_generator = QueryGenerator(llm=tool_llm)
query_generator(state["origin_query"])  # 根据原问题生成相关问题

result = [
    vector_store.query(query) for query in [state["origin_query"]] + state["similar_queries"]
]  # 根据原问题和生成的问题从向量数据库中检索
reranked_result = reciprocal_rank_fusion(result)  # 重排
```

# 服务相关
thrift文件放在thrifts文件夹下，在server.py和client.py已经实现了Unary RPC。
Server streaming RPC还需要实现。

启动服务（启动需要一点时间加载embedding模型）
```bash
python server.py
```
客户端使用
```bash
python client.py
```