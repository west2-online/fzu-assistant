from langchain.text_splitter import MarkdownTextSplitter
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import Chroma
import os

def split_and_save(file:str, db:Chroma = None, model:str = "embed-multilingual-light-v3.0") -> Chroma:
    cohere_embeddings = CohereEmbeddings(model = model)
    splitter = MarkdownTextSplitter(chunk_size = 500, chunk_overlap = 50)
    text = open(file, "r", encoding = "utf-8").read()
    chunks = splitter.split_text(text)
    # print(len(chunks))
    if(db == None):
        db = Chroma.from_texts(texts = chunks, embedding = cohere_embeddings, collection_name = "cohere_embed")
    else:
        db.add_texts(texts = chunks, embedding = cohere_embeddings, collection_name = "cohere_embed")
    return db

if __name__ == "__main__": # for Test

    query = "相关支持"

    vectorstores = split_and_save("./fzu-wiki-main/pages/index.mdx")

    res = vectorstores.similarity_search(query, k = 1)

    print(res)

    