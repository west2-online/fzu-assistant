from utils import DataLoader
from llms import zhipu
from embeddings import embeddings
from graph_store import GraphStore
from vector_store import VectorStore

# load data
loader = DataLoader("./data")
documents = loader.load_and_split()
print(len(documents))
print(documents)

# graph
graph_store = GraphStore(llm=zhipu)
graph_store.add_documents(documents)

graph_store.graph.refresh_schema()
print(graph_store.graph.schema)

print(graph_store.query("福州大学有哪些校区？"))

# vector
vector_store = VectorStore(embeddings=embeddings)
vector_store.add_documents(documents=documents)
print(vector_store.query("福州大学有哪些校区？"))
