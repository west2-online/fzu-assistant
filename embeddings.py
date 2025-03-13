# from langchain_huggingface import HuggingFaceEmbeddings

from langchain_community.embeddings import ZhipuAIEmbeddings
from config import conf

'''

model_name = conf.embedding_model
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    encode_kwargs=encode_kwargs
)

'''

embeddings = ZhipuAIEmbeddings(
    model="embedding-3",        # 使用智谱第三代嵌入模型[1](@ref)
    api_key=conf.zhipu.api_key  # 从配置读取API密钥
)

if __name__ == "__main__":
    print(embeddings.embed_query("你好"))
