from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
import re

class StepBackGenerator:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = self.create_prompt()
        self.generate_queries_chain = (
            self.prompt | self.llm | StrOutputParser()
        )

    def __call__(self, question: str) -> list:
        return self.generate_queries_chain.invoke({"question": question})

    def create_prompt(self):
        # Few Shot Examples
        examples = [
            {
                "input": "福州大学与清华大学有合作关系吗？",
                "output": "福州大学与哪些学校有合作关系？",
            },
            {
                "input": "福州大学是创建于新中国成立之后吗？",
                "output": "福州大学是哪年创建的",
            },
            {
                "input": "福州大学有电气工程与自动化学院吗？",
                "output": "福州大学都有哪些学院？",
            },
        ]
        # We now transform these to example messages
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )
        return ChatPromptTemplate.from_messages([
            ("system", '''
                您是一位**福州大学**相关知识的专家。您的任务是将问题“后退一步”，即将问题转述为更通用、更易回答的形式，但注意请尽量不要使问题与**福州大学**无关。
                注意：如果原始问题中含有“福州大学”相关字样，则后退一步后的问题也必须包含。
                以下是一些示例：
            '''),
            few_shot_prompt,
            ("user", "生成这个问题后退一步后的问题：{question}"),
        ])

if __name__ == "__main__":
    from langchain_community.chat_models import ChatZhipuAI
    tool_llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.5,
        zhipuai_api_key="9ace9999fd69cc6c5475bc6bd93d371a.SoY5YQwUwu5Y7fGC"
    )
    subquery_generate = StepBackGenerator(llm=tool_llm)
    print(subquery_generate("福州大学的校训是“明德至诚，博学远志”吗？"))