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
    1. 严格基于提供的schema生成Cypher查询
    2. **元素限制**：仅使用schema中明确定义的节点标签、关系类型和属性
    3. **搜索规范**：
       - 所有属性查询必须使用不区分大小写的模糊匹配，格式：`toLower(节点别名.属性) CONTAINS toLower('关键词')`
       - 禁止使用精确匹配(=)和全称匹配
    4. **别名规范**：
       - 所有节点必须使用明确别名（如：`(c:地点)`别名c）
       - 返回结果时始终使用别名引用属性（如：`c.name`）
    5. **聚合操作**：
       - 必须使用`COUNT(DISTINCT 别名)`进行计数
       - 避免重复计数和笛卡尔积
    6. **关系同义词**：将属于、拥有统一映射为`属于`关系
    7. **输出规范**：直接输出规范的Cypher语句，禁止包含额外解释

    ## Schema参考
    {schema}

    ## 生成示例（严格遵循的模板）
    示例1：
        用户输入: 铜盘校区配备的什么物品？
        Cypher语句: MATCH (p:地名 {{id: '铜盘'}})-[]->(i:物品) RETURN i.id
    示例2：
        用户输入: 介绍一下福州大学相关的东西
        Cypher语句: MATCH (fzu {{id: "福州大学"}})-[r]-(connected_node) RETURN fzu, type(r) AS relationship_type, connected_node
    示例3：
        用户输入：福州大学有哪些校区?
        Cypher语句：MATCH (fzu {{id: "福州大学"}})-[r]-(connected_node:地点) RETURN type(r) AS relationship_type, connected_node

    ## 待处理查询
    用户输入：{question}
    生成Cypher："""

    def __init__(self, llm):
        self.graph = Neo4jGraph(url=conf.neo4j.url,
                                username=conf.neo4j.username,
                                password=conf.neo4j.password,
                                database=conf.neo4j.database)
        self.graph_transformer = GraphTransformer(llm=llm)
        self.chain = GraphCypherQAChain.from_llm(
            llm, graph=self.graph, verbose=True, allow_dangerous_requests=True
        )
        self.few_shot_prompt = PromptTemplate(template=self.cypher_generate_prompt,
                                              input_variables=["question", "schema"])

    def add_documents(self, documents: t.List[Document]):
        graph_documents = self.graph_transformer.convert_to_graph_documents(documents)
        self.graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)

    def query(self, question: str):
        self.graph.refresh_schema()
        prompt = self.few_shot_prompt.format(question=question, schema=self.graph.schema)
        result = self.chain.invoke({"query": question}, prompt=prompt, return_only_outputs=True)
        return result

    def cypher(self, query: str):
        return self.graph.query(query)


if __name__ == "__main__":
    from llms import zhipu
    graph_store = GraphStore(llm=zhipu)
    print(graph_store.cypher("SHOW DATABASES"))  # Cypher
