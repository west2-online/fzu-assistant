from typing import Optional, List
from langchain.llms.base import LLM
from pydantic import Field

# 对chat_llm包装
class RunnableChatLLM(LLM):
    chat_llm: object = Field(...) # 不显式规定会报错 不知道为什么

    @property
    def _llm_type(self) -> str:
        return "runnable_chat_llm"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.chat_llm.chat(prompt) # 我一直得不到response 不知道_call应该怎么写
        if hasattr(response, "text"):
            return response.text
        return response

    class Config:
        arbitrary_types_allowed = True




import yaml
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from vector_store import VectorStore

from llms import chat_llm as original_chat_llm

class NaiveRAG:
    # 用langchain传
    def __init__(self, chat_llm, embeddings, vector_storage_dir, top_k):
        self.chat_llm = RunnableChatLLM(chat_llm=original_chat_llm)
        self.vector_store = VectorStore(
            embeddings=embeddings,
            storage_dir=vector_storage_dir,
            top_k=top_k
        )
        
        # 原来的 format_response 函数
        self.prompt = PromptTemplate(
            template=(
                "用户的问题是：{question}\n" # 原来 state 中的 origin_query，因为没有 state 就直接叫 question 了
                "请根据用户的问题，并且综合以下系统的搜索出的数据源的信息，不要做过多描述。\n"
                "请格外注意，如果涉及学校通知或者政策（如：保研，新生入学安排等），请直接将相关通知或政策的链接告知用户\n"
                "【向量数据库检索结果】\n"
                "{vector_results}"
            ),
            input_variables=["question", "vector_results"]
        )
        
        self.memory = ConversationBufferMemory( #原来的 state["history"]
            memory_key="chat_history",
            return_messages=True
        )

        self.llm_chain = LLMChain(
            llm=self.chat_llm,
            prompt=self.prompt, # 这个参数不知道有没有理解错
            memory=self.memory
        )
    
    def query(self, question: str) -> str:
        docs = self.vector_store.query(question)
        vector_results = yaml.dump([doc.page_content for doc in docs], allow_unicode=True)
        return self.llm_chain.run(question=question, vector_results=vector_results)
    
    def command_chat(self):
        # history 移到 self.memory 里
        print("\033[46m输入 'exit' 退出\033[0m")
        while (question := input("\033[36m输入：\033[0m")) != "exit":
            start = time.perf_counter()
            answer = self.query(question)
            print("\033[36m输出：\033[0m")
            print(answer)
            print(f"\033[36m耗时：\033[0m{time.perf_counter() - start}")
    
    def measure_speed(self, question="福州大学的校训是什么？"):
        for _ in range(10):
            start = time.perf_counter()
            _ = self.query(question)
            print(f"测试问题：{question} 耗时：{time.perf_counter()-start}")

if __name__ == "__main__":
    from llms import chat_llm
    from embeddings import embeddings
    from config import conf
    
    naive_rag = NaiveRAG( # 没改
        chat_llm=chat_llm,
        embeddings=embeddings,
        vector_storage_dir=conf.storage_dir.vector,
        top_k=conf.top_k
    )
    naive_rag.command_chat()
