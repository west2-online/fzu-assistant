from tqdm import trange
from utils import VectorStore
from embeddings import embeddings
from utils import DataLoader
from config import conf


def train_notice(batch=10000):
    vector_store = VectorStore(embeddings=embeddings, 
                               storage_dir=conf.storage_dir.notice)

    notice_loader = DataLoader(conf.data_dir.notice)
    notice_documents = notice_loader.load_and_split()
    QA_loader = DataLoader(conf.data_dir.QA)
    QA_documents = QA_loader.load_and_split()
    documents = notice_documents + QA_documents
    for batch_num, i in enumerate(trange(0, len(documents), batch), start=1):
        chunk_documents = documents[i:i+batch]
        vector_store.add_documents(documents=chunk_documents)

    print("done")


if __name__ == "__main__":
    train_notice()
    vector_store = VectorStore(embeddings=embeddings, 
                               storage_dir=conf.storage_dir.notice)
    vector_store.command_search()
