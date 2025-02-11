from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from config import conf
from langchain_community.chat_models import ChatZhipuAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


tool_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.tool_llm,
    task="text-generation",
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03,
    ),
)
tool_llm = ChatHuggingFace(llm=tool_llm)

chat_llm = HuggingFacePipeline.from_model_id(
    model_id=conf.chat_llm,
    task="text-generation",
    pipeline_kwargs=dict(
        max_new_tokens=4096,
        repetition_penalty=1.03,
    ),
)
chat_llm = ChatHuggingFace(llm=chat_llm)

def query_stream(llm, question: str):
  for chunk in llm.stream(question):
      content = chunk.content
      if content:
          yield content

if __name__ == "__main__":
    question = "你觉得人生是什么"
    for answer in query_stream(tool_llm, question):
        print(answer)
