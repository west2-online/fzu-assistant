from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss
from tqdm import trange

import typing as t
import os


class VectorStore:
    def __init__(self, embeddings, storage_dir, top_k=10):
        self.top_k = top_k
        self.storage_dir = storage_dir
        dim = len(embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(dim)  # cpu index
        if "index.faiss" not in os.listdir(storage_dir):
            self.vector_store = FAISS(
                embedding_function=embeddings,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )
        else:
            self.vector_store = FAISS.load_local(
                folder_path=storage_dir,
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )


    def add_documents(self, documents: t.List[Document]):
        self.vector_store.add_documents(documents)

    def query(self, question: str) -> t.List[Document]:
        return self.vector_store.similarity_search(question, k=self.top_k)
        # return self.vector_store.similarity_search_with_score(question, k=self.top_k)
        
    def save(self, storage_dir=None):
        if storage_dir is None:
            storage_dir = self.storage_dir
        self.vector_store.save_local(storage_dir)
    
    def command_search(self):
        while (inp:=input("检索：")) != "exit":
            res = self.query(inp)
            for r in res:
                # print(r.page_content)
                print(r)

    def train(self, documents: t.List[Document], batch=100):
        for i in trange(0, len(documents), batch):
            chunk_documents = documents[i:i+batch]
            self.add_documents(documents=chunk_documents)
            self.save()


if __name__ == "__main__":
    from utils import DataLoader
    from embeddings import embeddings
    from config import conf
    loader = DataLoader(data_dir=conf.data_dir.whole)
    documents = loader.load_and_split()
    vector_store = VectorStore(embeddings=embeddings, storage_dir=conf.storage_dir.vector)
    vector_store.train(documents=documents)
    print(vector_store.query("福州大学创建多少年了？"))
    vector_store.command_search()
