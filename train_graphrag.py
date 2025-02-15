from tqdm import trange
from utils import GraphStore, DataLoader
from llms import tool_llm
from config import conf


def train_QA(batch=10):
    graph_store = GraphStore(llm=tool_llm, 
                             url=conf.neo4j.url,
                             username=conf.neo4j.username,
                             password=conf.neo4j.password)
    QA_loader = DataLoader(conf.data_dir.QA)
    documents = QA_loader.load_and_split()
    for batch_num, i in enumerate(trange(0, len(documents), batch), start=1):
        chunk_documents = documents[i:i+batch]
        try:
            graph_store.add_documents(documents=chunk_documents)
        except:
            try: 
                graph_store.add_documents(documents=chunk_documents)
            except:
                continue
            
    print("done")


if __name__ == "__main__":
    train_QA()
    graph_store = GraphStore(llm=tool_llm, 
                             url=conf.neo4j.url,
                             username=conf.neo4j.username,
                             password=conf.neo4j.password)
    graph_store.command_search()