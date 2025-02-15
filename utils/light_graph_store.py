from lightrag import LightRAG as LightRAG, QueryParam
from lightrag.llm.hf import hf_model_complete, hf_embed
from lightrag.utils import EmbeddingFunc
from langchain_core.documents import Document
from transformers import AutoModel, AutoTokenizer

import typing as t


class LightGraphStore:
    def __init__(self, working_dir, llm_id, embedding_id, query_mode="mix", top_k=10, log_level="ERROR"):
        self.lightrag = LightRAG(
            working_dir=working_dir,
            log_level=log_level,
            vector_storage="FaissVectorDBStorage",
            graph_storage="Neo4JStorage",
            llm_model_func=hf_model_complete,
            llm_model_name=llm_id,
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=4096,
                func=lambda texts: hf_embed(
                    texts,
                    tokenizer=AutoTokenizer.from_pretrained(embedding_id, model_max_length=512),
                    embed_model=AutoModel.from_pretrained(embedding_id)
                )
            ),
            addon_params={
                "insert_batch_size": 50
            }
        )

        self.query_param = QueryParam(mode=query_mode, only_need_context=True, top_k=top_k)
    
    def insert(self, documents: t.Union[t.List[str], t.List[Document]]):
        if isinstance(documents[0], Document):
            documents = [doc.page_content for doc in documents]
        self.lightrag.insert(documents)

    def query(self, query: str):
        result = self.lightrag.query(query=query, param=self.query_param)
        return result

    def command_search(self):
        while (inp:=input("检索：")) != "exit":
            res = self.query(query=inp)
            res


if __name__ == "__main__":
    from config import conf
    from utils import DataLoader
    QA_loader = DataLoader(conf.data_dir.QA)
    documents = QA_loader.load_and_split()
    # print(documents[0].page_content)
    light_rag_store = LightGraphStore(
        working_dir=conf.storage_dir.QA,
        llm_id=conf.tool_llm,
        embedding_id=conf.embedding_model,
        query_mode=conf.lightrag_query_mode,
        top_k=conf.top_k
    )
    light_rag_store.insert(documents)

    print(light_rag_store.query(query="福州大学有什么学院?"))

