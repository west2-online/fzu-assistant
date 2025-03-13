from .zhipuai import ZhipuAIChat


tool_llm = ZhipuAIChat(model_name="glm-3-turbo")  # 工具模型
chat_llm = ZhipuAIChat(model_name="glm-4")        # 对话模型