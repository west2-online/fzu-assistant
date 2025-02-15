from utils import LightGraphStore
from utils import DataLoader
from config import conf


def train_QA(batch=50):
    light_rag_store = LightGraphStore(
        working_dir=conf.storage_dir.QA,
        llm_id=conf.tool_llm,
        embedding_id=conf.embedding_model,
        query_mode=conf.lightrag_query_mode,
        top_k=conf.top_k
    )
    QA_loader = DataLoader(conf.data_dir.QA)
    documents = QA_loader.load_and_split()
    light_rag_store.insert(documents)
    print("done")


if __name__ == "__main__":
    train_QA()
    light_rag_store = LightGraphStore(
        working_dir=conf.storage_dir.QA,
        llm_id=conf.tool_llm,
        embedding_id=conf.embedding_model,
        query_mode=conf.lightrag_query_mode,
        top_k=conf.top_k
    )
    light_rag_store.command_search()