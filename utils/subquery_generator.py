from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate
import re

class SubProblemGenerator:
    def __init__(self, llm, isSequence:bool):
        self.llm = llm
        if(isSequence):
            self.prompt = self.create_sequence_prompt()
        else:
            self.prompt = self.create_individual_prompt()
        self.generate_queries_chain = (
            self.prompt | self.llm | StrOutputParser() | self.extract_question | (lambda x: x.split("\n"))
        )
    
    def __call__(self, question: str) -> list:
        return self.generate_queries_chain.invoke({"question": question})

    def create_sequence_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", '''
            你将被要求将一个复杂的问题分解为多个互相关联、递进的子问题。每个子问题的解答会帮助解答下一个子问题，直到最后一个子问题帮助回答原始问题。

            请遵循以下指导原则：
            1. **递归拆解**：每个子问题的解答应该为下一个子问题提供必要的信息。确保问题之间是递进的，每个子问题的答案逐步帮助接近原始问题的解答。
            2. **简洁明了**：每个子问题应该简洁、清晰，并且不应过于复杂。尽量避免生成冗长或不明确的问题，减少生成不必要的问题。
            3. **递进性**：第一个子问题的答案应该为第二个子问题提供线索，第二个子问题的答案为第三个子问题提供线索，以此类推，直到最后一个子问题可以帮助解决原始问题。
            4. **格式化输出**：生成的子问题应当以列表形式输出，每个子问题为一个字符串，单独占一行，不要有其他额外输出，**不要输出编号**。
            5. **生成数量**：根据原始问题难易程度可以生成不同数量的子问题，请控制生成的数量，但是至少生成一个子问题，且不要生成超过三个子问题。
            '''),
            ("system", """输出格式为
             ```question
             xxx
             xxx
             ```
             """),
            ("user", "请将以下问题拆解为多个相关子问题：{question}"),
        ])
    
    def create_individual_prompt(self):
        return ChatPromptTemplate.from_messages([
            ("system", '''
            你将被要求将一个复杂的问题分解为多个可独立解决的子问题。每个子问题应该尽可能简洁、独立且具体，确保它们可以单独解决，最终合并答案来帮助回答原始问题。

            请遵循以下指导原则：
            1. **问题拆解**：根据问题的复杂性和不同层面，生成多个子问题。例如，如果问题包含多个方面，应该为每个方面生成一个子问题。
            2. **子问题简洁明了**：每个子问题应该足够简短，易于理解和回答。不要将过于复杂的问题作为子问题，尽量将其分解为简单问题。
            3. **可解性**：每个子问题都应该可以被独立解决，并且不依赖于其他子问题的答案。
            4. **明确子问题的目标**：确保每个子问题的目标是明确的，以便于回答时能为最终答案提供有价值的信息。
            5. **生成数量**：根据原始问题难易程度可以生成不同数量的子问题，请控制生成的数量，但是至少生成一个子问题，且不要生成超过四个子问题。
            '''),
            ("system", """输出格式为
             ```question
             xxx
             xxx
             ```
             """),
            ("user", "请将以下问题拆解为多个相关子问题：{question}"),
        ])
    
    @staticmethod
    def extract_question(text: str) -> str:
        pattern = r'(?s)```question\s*(.*?)\s*```'
        matches = re.findall(pattern, text)
    
        if matches:
            return matches[-1].strip()
        
        # 如果正则匹配失败，返回原始文本
        return text.strip()

if __name__ == "__main__":
    from langchain_community.chat_models import ChatZhipuAI
    tool_llm = ChatZhipuAI(
        model="glm-4",
        temperature=0.5,
        zhipuai_api_key="9ace9999fd69cc6c5475bc6bd93d371a.SoY5YQwUwu5Y7fGC"
    )
    subquery_generate = SubProblemGenerator(llm=tool_llm, isSequence = True)
    print(subquery_generate("福州大学的学生需要记住福州大学的校训吗？"))