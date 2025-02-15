from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from config import conf
from langchain_community.chat_models import ChatZhipuAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# huggingface version
# ====================================================
tool_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.tool_llm,
    task="text-generation",
    device_map="auto",
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03
    ),
)
tool_llm = ChatHuggingFace(llm=tool_llm)

chat_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.chat_llm,
    task="text-generation",
    device_map="auto",
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03
    ),
)
chat_llm = ChatHuggingFace(llm=chat_llm)
# ====================================================

# vllm client
# ====================================================
# from langchain_community.llms import VLLMOpenAI
# llm = VLLMOpenAI(
#     openai_api_key="EMPTY",
#     openai_api_base="http://localhost:8000/v1",
#     model_name="/home/xezx/AI_answer/demo3/models/DeepSeek-R1-Distill-Qwen-7B"
# )
# ====================================================

# vllm version
# ====================================================
# from langchain_community.llms.vllm import VLLM
# chat_llm = VLLM(
#     model=conf.chat_llm,
#     tensor_parallel_size=2,
#     max_new_tokens=4096,
#     top_k=10,
#     top_p=0.95,
#     temperature=0.8
# )
# tool_llm = VLLM(
#     model=conf.tool_llm,
#     tensor_parallel_size=2,
#     max_new_tokens=4096,
#     top_k=10,
#     top_p=0.95,
#     temperature=0.8
# )
# ====================================================


def query_stream(llm, question: str):
  for chunk in llm.stream(question):
      content = chunk.content if isinstance(llm, ChatHuggingFace) else chunk
      if content:
          yield content

if __name__ == "__main__":
    while (question:=input("输入：")) != "exit":
        for answer in query_stream(tool_llm, question):
            print(answer, end="")
