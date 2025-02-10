from langchain_core.prompts.prompt import PromptTemplate
import re


class QuestionCompleter:

    def __init__(self, llm):
        self.llm = llm
        self.prompt = self.create_prompt()

    @staticmethod
    def create_prompt():
        prompt = """
        用户的问题存在模糊的部分。
        你试图从信息完整性，语义歧义性，上下文依赖度，领域特异性来进行分析，猜测用户问题缺少的成分，尝试给出5个用户可能希望问的问题。
        输出格式严格按照一下规范，只要输出预测的问题即可。

        输出示例：
        ```answer
        1. 补全的问题
        2. 补全的问题
        3. 补全的问题
        ```
        用户的问题为：{question}
        输出回答：
        """

        return PromptTemplate.from_template(prompt)

    @staticmethod
    def extract_answer(text) -> dict:
        pattern = r'(?i)```\s*answer\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            return None
        answer = matches[-1].strip()
        return answer

    def __call__(self, question):
        prompt = self.prompt.format(question=question)
        result = self.llm.invoke(prompt)
        result = self.extract_answer(result.content)
        result = f"""同学您的问题可能有一些模糊，可以尝试补全一些信息，或者尝试问问:
        {result}
        """
        return result
