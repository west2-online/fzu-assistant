from graph_store import GraphStore
from vector_store import VectorStore
from llms import tool_llm
from embeddings import embeddings
from utils import DataLoader
from config import conf

def train():
    graph_store = GraphStore(llm=tool_llm)
    vector_store = VectorStore(embeddings=embeddings)

    loader = DataLoader(conf.data_dir)
    documents = loader.load_and_split()
    vector_store.add_documents(documents=documents)
    for batch_num, i in enumerate(range(0, len(documents), 10), 1):
        chunk_documents = documents[i:i+10]
        print(f"第 {batch_num} 批数据")
        print("vector done")
        try:
            graph_store.add_documents(documents=chunk_documents)
        except Exception as e:
            try:
                graph_store.add_documents(documents=chunk_documents)
            except Exception as e:
                continue
        print("graph done")


if __name__ == "__main__":
    train()