from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
from config import conf
from langchain_mistralai import ChatMistralAI
from langchain_community.chat_models import ChatZhipuAI


# llm = HuggingFacePipeline.from_model_id(
#     model_id=conf.llm,
#     task="text-generation",
#     pipeline_kwargs=dict(
#         max_new_tokens=2048,
#         repetition_penalty=1.03,
#     ),
# )
# llm = ChatHuggingFace(llm=llm)


mistral = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0,
    max_retries=2
)

zhipu = ChatZhipuAI(
    model="glm-4",
    temperature=0.5,
    zhipuai_api_key=conf.ZHIPUAI_API_KEY
)


if __name__ == "__main__":
    print(zhipu.invoke("你好"))
