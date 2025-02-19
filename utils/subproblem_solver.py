from langchain_core.documents import Document
import yaml
from vector_store import VectorStore

class SubProblemSolver:
    def __init__(self, llm, rerank = None):
        self.llm = llm
        self.rerank = rerank

    def __call__(self, query:str, last_answer:str, vector_store:VectorStore) -> str:
        res = vector_store.query(query)
        if(last_answer):
            res.append(Document(
                page_content = last_answer
            ))#将上一个答案加入查询结果中
        result = yaml.dump([doc.page_content for doc in res], allow_unicode=True)
        if(self.rerank is not None):
            result = self.rerank(query, result)
        return self.generate_answer(query, result)
    
    def generate_answer(self, query:str, result:str) -> str:
        prompt = f"""
        用户的问题是：{query}
        请根据用户的问题，并且综合以下系统的搜索出的数据源的信息，不要做过多描述。
        请格外注意，如果涉及学校通知或者政策（如：保研，新生入学安排等），请直接将相关通知或政策的链接告知用户
        【向量数据库检索结果】
        {result}
        """
        answer = ""
        for chunk in self.llm.stream(prompt):
            content = chunk
            if content:
                answer += content
        return answer

if __name__ == '__main__':
    from llms import tool_llm
    from embeddings import embeddings
    from config import conf
    sps = SubProblemSolver(tool_llm)
    print(sps(query = "福州大学的校训是什么？", last_answer = "", 
              vector_store = VectorStore(embeddings=embeddings, 
                                        storage_dir=conf.storage_dir.vector,
                                        top_k=conf.top_k)))