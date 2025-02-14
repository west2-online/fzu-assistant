from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

import typing as t
import os


class VectorStore:
    def __init__(self, embeddings, storage_dir, top_k=10):
        self.top_k = top_k
        self.storage_dir = storage_dir
        dim = len(embeddings.embed_query("hello world"))
        index = faiss.IndexFlatL2(dim)  # cpu index
        if len(os.listdir(storage_dir)) == 0:
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
        self.save()

    def query(self, question: str) -> t.List[Document]:
        return self.vector_store.similarity_search(question, k=self.top_k)
    
    def save(self, storage_dir=None):
        if storage_dir is None:
            storage_dir = self.storage_dir
        self.vector_store.save_local(storage_dir)
    
    def command_search(self):
        while (inp:=input("检索：")) != "exit":
            res = self.query(inp)
            for r in res:
                print(r.page_content)


if __name__ == "__main__":
    from embeddings import embeddings
    vector_store = VectorStore(embeddings=embeddings)

    document_1 = Document(page_content="foo", metadata={"baz": "bar"})
    document_2 = Document(page_content="thud", metadata={"bar": "baz"})
    document_3 = Document(page_content="i will be deleted :(")

    documents = [document_1, document_2, document_3]
    vector_store.add_documents(documents=documents)
    print(vector_store.query("我要被开了"))
    vector_store.save("./vector_storage")

    new_vector_store = VectorStore(embeddings=embeddings, storage_dir="./vector_storage")
    print(vector_store.query("我要被开了"))
