from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import re


class QueryGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.query_num = 4
        self.prompt = self.create_prompt()
        self.generate_queries_chain = (
            self.prompt | self.llm | StrOutputParser() | self.extract_question | (lambda x: x.split("\n"))
        )

    def __call__(self, question: str) -> list:
        return self.generate_queries_chain.invoke({"question": question})

    def create_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", "你是一个的助手，能够根据用户提供的查询生成多个相关的搜索问题"),
            ("system", """输出格式为
             ```question
             xxx
             xxx
             ```
             """),
            ("user", "请生成与以下主题相关的多个搜索问题：{question}"),
            ("user", f"输出格式（{self.query_num}个问题）：")
        ])
    
    @staticmethod
    def extract_question(text) -> dict:
        pattern = r'(?i)```\s*question\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            return None
        question = matches[-1].strip()
        return question
    
    
if __name__ == "__main__":
    from langchain_community.chat_models import ChatZhipuAI
    tool_llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.5,
        zhipuai_api_key="9ace9999fd69cc6c5475bc6bd93d371a.SoY5YQwUwu5Y7fGC"
    )
    query_generate = QueryGenerator(llm=tool_llm)
    print(query_generate("福州大学食堂"))
    print(query_generate("保研"))

