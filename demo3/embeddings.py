from langchain_huggingface import HuggingFaceEmbeddings
from config import conf


model_name = conf.embeddings
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    encode_kwargs=encode_kwargs
)