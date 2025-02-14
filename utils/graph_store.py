""" deprecated """

from langchain_core.documents import Document
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.messages.ai import AIMessage
from retry import retry
import typing as t
import re
from .graph_transformer import GraphTransformer


class GraphStore:

    def __init__(self, llm, url, username, password):
        self.llm = llm
        self.graph = Neo4jGraph(url=url,
                                username=username,
                                password=password)
        self.graph_transformer = GraphTransformer(llm=llm)
        self.few_shot_prompt = self.create_prompt()
        self.chain = self.few_shot_prompt | self.llm | self.extract_cypher | self.cypher


    def add_documents(self, documents: t.List[Document]):
        graph_documents = self.graph_transformer.convert_to_graph_documents(documents)
        self.graph.add_graph_documents(graph_documents, baseEntityLabel=True, include_source=True)

    def query(self, question: str):
        @retry(tries=3)
        def _query(question: str):
            result = self.chain.invoke({"question": question}, return_only_outputs=True)
            return result
        try:
            result = _query(question)
        except Exception as e:
            result = {}
        return result

    def cypher(self, query: str) -> list:
        # print(query)
        return self.graph.query(query)

    def create_prompt(self):
        cypher_generate_prompt = """
        # Cypher生成任务
        ## 指令要求
        1. 严格基于提供的schema生成Cypher查询, Cypher尽可能简单
        2. **元素限制**：
        - 不要对节点的标签做筛选，只匹配id
        - 不要对节点之间的关系进行筛选，使用"-[r]-"的表达。禁止明确声明关系的匹配(禁止如：-[r:包括]->)
        3. **搜索规范**：
        - 禁止使用精确匹配(=)和全称匹配
        4. **别名规范**：
        - 所有节点必须使用明确别名（如：`(c:地点)`别名c）
        5. **输出规范**：直接输出规范的Cypher语句，禁止包含额外解释


        ## 生成示例（严格遵循的模板）
        示例1：
            用户输入: 铜盘校区配备的什么物品？
            Cypher语句: 
            ```cypher
            MATCH (p: {{id: '铜盘'}})-[r]-(v) RETURN p, r, v;
            ```
        示例2：
            用户输入: 介绍一下福州大学相关的东西
            ```cypher
            Cypher语句: MATCH (fzu {{id: "福州大学"}})-[r]-(v) RETURN fzu, r, v;
            ```
        示例3：
            用户输入：福州大学有哪些校区?
            ```cypher
            Cypher语句：MATCH (fzu {{id: "福州大学"}})-[r]-(v) WHERE v.id CONTAINS "校区" RETURN fzu, r, v;
            ```

        ## 待处理查询
        用户输入：{question}
        Cypher语句："""
        return PromptTemplate(template=cypher_generate_prompt, input_variables=["question"])

    @staticmethod
    def extract_cypher(result: t.Union[AIMessage, str]) -> str:
        text = result if isinstance(result, str) else result.content
        pattern = r'(?i)```\s*cypher\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[-1].strip()


if __name__ == "__main__":
    from llms import tool_llm
    graph_store = GraphStore(llm=tool_llm)
    result = graph_store.cypher("show databases;")
    print(result)
