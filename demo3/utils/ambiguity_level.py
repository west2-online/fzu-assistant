from langchain_core.prompts.prompt import PromptTemplate
import json
import re


class AmbiguityLevel:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = self.create_prompt()

    def __call__(self, question: str):
        prompt = self.prompt.format(question=question)
        result = self.llm.invoke(prompt)
        score = self.extract_json(result.content).get("总分")
        level = self.level(score)
        return level

    @staticmethod
    def level(score):
        if score >= 4:
            return 3  # 追问信息
        elif 2.9 <= score < 4:
            return 2  # 猜测并生成问题，再进行回答
        elif score < 2.9:
            return 1  # 直接回答

    @staticmethod
    def create_prompt():
        ambiguity_score_prompt = """
        用户问题为：{question}。请根据以下规则对用户问题进行模糊程度打分。
        模糊问题评分标准
        请根据以下维度对用户问题进行模糊评分（1-5分，1=非常清晰，5=极度模糊），并给出总分和优化建议：
        1. 信息完整性 🔍
        5分：仅包含1个核心词（如"怎么办？"）
        3分：有主题但缺少关键要素（如"电脑坏了"）
        1分：包含时间、地点、错误代码等细节（如"Win11更新后USB接口失灵"）

        2. 语义歧义性 🤔
        5分：存在≥2种合理解释（如"苹果不能吃"）
        3分：需猜测领域（如"求解决方案"）
        1分：明确指向特定领域（如"Python正则表达式匹配失败"）

        3. 上下文依赖度 🧩
        5分：必须依赖未提及的上下文（如"老问题又出现了"）
        3分：需假设部分场景（如"安装失败"）
        1分：自包含完整上下文（如"用Anaconda安装TensorFlow 2.10时报SSL错误"）

        4. 领域特异性 🎯
        5分：泛领域问题（如"怎么学习？"）
        3分：宽泛领域问题（如"代码有问题"）
        1分：细分领域问题（如"React Native 0.71版本iOS模拟器编译卡在PhaseScriptExecution"）

        计算规则
        权重分配：
        总分 = 信息完整性×40% + 语义歧义性×30% + 上下文依赖度×20% + 领域特异性×10%

        输出结果：
        ```json
        {{"总分": [分数]}}
        ```
        """

        return PromptTemplate.from_template(ambiguity_score_prompt)

    @staticmethod
    def extract_json(text) -> dict:
        pattern = r'(?i)```\s*json\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL)

        if not matches:
            return None
        last_json_str = matches[-1].strip()

        try:
            return json.loads(last_json_str)
        except json.JSONDecodeError:
            # 处理可能存在的格式错误
            try:
                # 尝试修复常见的尾部逗号问题
                fixed = re.sub(r',\s*}', '}', re.sub(r',\s*]', ']', last_json_str))
                return json.loads(fixed)
            except json.JSONDecodeError:
                return None
