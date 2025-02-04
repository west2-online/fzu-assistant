from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_neo4j import GraphCypherQAChain


class GraphRetriever:
    few_shot_examples = [
        {
            "question": "铜盘校区配备的什么物品？",
            "query": "MATCH (p:地名 {id: '铜盘'})-[:配备]->(i:物品) RETURN i.id, i.type",
        },
        {
            "question": "去旗山需要什么物品?",
            "query": "MATCH (p:地名 {id: '旗山'})-[:需要]->(i:物品) RETURN i.id, i.type",
        },
        {
            "question": "智汇福大 app 上要请谁来报修?",
            "query": "MATCH (a:应用 {id: '智汇福大app'})-[:报修]->(v:职业) RETURN v.id, v.type",
        }
    ]
    cypher_generate_prompt = """任务：严格根据提供的模式和说明生成用于查询图数据库的 Cypher 语句。
    说明：
    仅使用模式中提及的节点、关系和属性。
    始终将 Cypher 输出用三个反引号括起来。反引号后面不要添加 'cypher'。
    对于任何与属性相关的搜索，始终进行不区分大小写的模糊搜索。例如：要搜索公司名称，请使用 toLower(c.name) contains 'neo4j'。
    在查询中始终使用别名来引用节点。
    对于聚合操作，始终返回 count (DISTINCT n) 以避免重复。
    OWNS_STOCK_IN 关系与 OWNS 和 OWNER 同义。
    使用下面的问题示例和准确的 Cypher 语句作为指导。
    模式：
    {schema}
    示例：以下是针对特定问题生成的一些 Cypher 语句示例："""

    def __init__(self, llm, embeddings, graph, vector_store):
        self.graph = graph
        self.chain = GraphCypherQAChain.from_llm(
            llm, graph=graph, verbose=True, allow_dangerous_requests=True
        )
        self.example_selector = SemanticSimilarityExampleSelector.from_examples(
            self.few_shot_examples,
            embeddings,
            vector_store,
            k=5,
            input_keys=["question"],
        )
        self.few_shot_prompt = FewShotPromptTemplate(
            example_selector=self.example_selector,
            example_prompt=PromptTemplate.from_template("用户输入: {question}\nCypher语句: {query}"),
            prefix=self.cypher_generate_prompt,
            suffix="用户输入: {question}\nCypher 语句: ",
            input_variables=["schema", "question"],
        )

    def query(self, question: str) -> str:
        self.graph.refresh_schema()
        prompt = self.few_shot_prompt.format(question=question, schema=self.graph.schema)
        chain_result = self.chain.invoke({"query": question}, prompt=prompt, return_only_outputs=True)
        result = chain_result.get("result", None)
        result = "对不起，没有找到相关回答" or result
        return result
