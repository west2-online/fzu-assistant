from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings import ZhipuAIEmbeddings
from config import conf


# model_name = conf.embedding_model
# encode_kwargs = {'normalize_embeddings': False}
# embeddings = HuggingFaceEmbeddings(
#     model_name=model_name,
#     encode_kwargs=encode_kwargs
# )


embeddings = ZhipuAIEmbeddings(
    model="embedding-3",
    api_key=conf.ZHIPUAI_API_KEY
)

if __name__ == "__main__":
    print(embeddings.embed_query("你好"))
