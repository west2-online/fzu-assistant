from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from config import conf
from langchain_community.chat_models import ChatZhipuAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


tool_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.tool_llm,
    task="text-generation",
    device=0,
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03
    ),
)
tool_llm = ChatHuggingFace(llm=tool_llm)

chat_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.chat_llm,
    task="text-generation",
    device=1,
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03
    ),
)
chat_llm = ChatHuggingFace(llm=chat_llm)


# from langchain_community.llms import VLLMOpenAI

# llm = VLLMOpenAI(
#     openai_api_key="EMPTY",
#     openai_api_base="http://localhost:8000/v1",
#     model_name="/home/xezx/AI_answer/demo3/models/DeepSeek-R1-Distill-Qwen-7B"
# )


def query_stream(llm, question: str):
  for chunk in llm.stream(question):
      content = chunk.content
      if content:
          yield content

if __name__ == "__main__":
    question = "你觉得人生是什么"
    for answer in query_stream(llm, question):
        print(answer, end="")
    print(llm.invoke(question))
