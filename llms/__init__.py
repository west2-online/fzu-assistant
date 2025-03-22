from .vllm_llm import VLLMClient

chat_llm = VLLMClient(
    model="chat_llm",
    temperature=0,
    max_retries=2,
    api_key="EMPTY",
    base_url="http://localhost:8000/v1"
)

from .zhipu_llm import zhipu_llm

tool_llm = zhipu_llm
