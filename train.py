from graph_store import GraphStore
from vector_store import VectorStore
from llms import tool_llm
from embeddings import embeddings
from config import conf

def train():
    graph_store = GraphStore(llm=tool_llm)
    vector_store = VectorStore(embeddings=embeddings)

    loader = DataLoader(conf.data_dir)
    documents = loader.load_and_split()
    vector_store.add_documents(documents=documents)
    graph_store.add_documents(documents=documents)