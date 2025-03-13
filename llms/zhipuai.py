from zhipuai import ZhipuAI
import os
from config import conf

class ZhipuAIChat:
    def __init__(self, model_name: str = "glm-4"):
        self.client = ZhipuAI(api_key = conf.zhipu.api_key)
        self.model_name = model_name

    def stream(self, prompt: str, history: list = None) -> str:
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True,
            max_tokens=4096,  # 对应原代码的max_new_tokens
            temperature=0.7   # 可自定义调节参数
        )
        for chunk in response:
            yield chunk.choices[0].delta.content

    def invoke(self, prompt: str, history: list = None) -> str:
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=False,
            max_tokens=4096,
            temperature=0.7
        )
        return response.choices[0].message.content

def get_llms():
    # 使用同一个模型的不同版本（或不同参数）
    tool_llm = ZhipuAIChat(model_name="glm-3-turbo")  # 工具模型
    chat_llm = ZhipuAIChat(model_name="glm-4")        # 对话模型
    return tool_llm, chat_llm