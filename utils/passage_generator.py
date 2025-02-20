from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
import re

class PassageGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = self.create_prompt()
        self.generate_queries_chain = (
            self.prompt | self.llm | StrOutputParser()
        )

    def __call__(self, question: str) -> list:
        return self.generate_queries_chain.invoke({"question": question})

    def create_prompt(self):
        
        return ChatPromptTemplate.from_messages([
            ("system", '''
                请以你已有的知识回答用户的问题，保持回答清晰简洁，不要有过多赘述。
                回答时请直接给出答案，不要复述问题。
                如果你并不知道问题的答案，可以编一个。
            '''),
            ("user", "用户的问题：{question}"),
        ])

if __name__ == "__main__":
    from langchain_community.chat_models import ChatZhipuAI
    tool_llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.5,
        zhipuai_api_key="9ace9999fd69cc6c5475bc6bd93d371a.SoY5YQwUwu5Y7fGC"
    )
    subquery_generate = PassageGenerator(llm=tool_llm)
    print(subquery_generate("福州大学的校训是什么？"))