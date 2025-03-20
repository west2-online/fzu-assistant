from langchain_openai import ChatOpenAI


class VLLMClient(ChatOpenAI):
    @property
    def _llm_type(self):
        return "chat_llm"

llm = VLLMClient(
    model="chat_llm",
    temperature=0,
    max_retries=2,
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)
