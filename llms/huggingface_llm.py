from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
import typing as t

def get_llms(model_ids: t.List):
    tool_llm = HuggingFacePipeline.from_model_id(
        model_id=model_ids[2],
        task="text-generation",
        device_map="auto",
        pipeline_kwargs=dict(
            max_new_tokens=4096,
            repetition_penalty=1.03
        ),
    )
    tool_llm = ChatHuggingFace(llm=tool_llm)

    chat_llm = HuggingFacePipeline.from_model_id(
        model_id=model_ids[1],
        task="text-generation",
        device_map="auto",
        pipeline_kwargs=dict(
            max_new_tokens=4096,
            repetition_penalty=1.03
        ),
    )
    chat_llm = ChatHuggingFace(llm=chat_llm)