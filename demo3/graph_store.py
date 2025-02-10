from langchain_core.documents import Document
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
import typing as t
from utils import GraphTransformer
from config import conf


class GraphStore:
    cypher_generate_prompt = """# Cypher生成任务
    ## 指令要求
    1. 严格基于提供的schema生成Cypher查询, Cypher尽可能简单
    2. **元素限制**：
       - 不要对节点的标签做筛选，只匹配id
       - 不要对节点之间的关系进行筛选，使用"-[r]-"的表达。禁止明确声明关系的匹配(禁止如：-[r:包括]->)
    3. **搜索规范**：
       - 禁止使用精确匹配(=)和全称匹配
    4. **别名规范**：
       - 所有节点必须使用明确别名（如：`(c:地点)`别名c）
       - 返回结果时始终使用别名引用属性（如：`c.name`）
    5. **输出规范**：直接输出规范的Cypher语句，禁止包含额外解释

    ## Schema参考
    {schema}

    ## 生成示例（严格遵循的模板）
    示例1：
        用户输入: 铜盘校区配备的什么物品？
        Cypher语句: MATCH (p: {{id: '铜盘'}})-[r]-(v) RETURN p, r, v
    示例2：
        用户输入: 介绍一下福州大学相关的东西
        Cypher语句: MATCH (fzu {{id: "福州大学"}})-[r]-(v) RETURN fzu, r, v
    示例3：
        用户输入：福州大学有哪些校区?
        Cypher语句：MATCH (fzu {{id: "福州大学"}})-[r]-(v) WHERE v.id CONTAINS "校区" RETURN fzu, r, v;

    ## 待处理查询
    用户输入：{question}
    生成Cypher："""

    def __init__(self, llm):
        self.graph = Neo4jGraph(url=conf.neo4j.url,
                                username=conf.neo4j.username,
                                password=conf.neo4j.password,
                                database=conf.neo4j.database)
        self.graph_transformer = GraphTransformer(llm=llm)
        self.few_shot_prompt = PromptTemplate(template=self.cypher_generate_prompt,
                                              input_variables=["question", "schema"])
        self.chain = GraphCypherQAChain.from_llm(
            llm, graph=self.graph, return_direct=True, return_intermediate_steps=True,
            cypher_prompt=self.few_shot_prompt, verbose=False,
            allow_dangerous_requests=True, validate_cypher=True
        )

    def add_documents(self, documents: t.List[Document]):
        graph_documents = self.graph_transformer.convert_to_graph_documents(documents)
        self.graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)

    def query(self, question: str):
        result = self.chain.invoke({"query": question}, return_only_outputs=True)
        return result

    def cypher(self, query: str):
        return self.graph.query(query)
