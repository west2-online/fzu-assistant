
import thriftpy2
from thriftpy2.rpc import make_server

from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from RAGFusion import RAGFusion
rag_fusion = RAGFusion(chat_llm=chat_llm,
                        tool_llm=tool_llm,
                        embeddings=embeddings,
                        vector_storage_dir=conf.storage_dir.vector,
                        top_k=conf.top_k)
class ChatServiceHandler:
    def chat(self, query):
        return rag_fusion.query(query)
    
chat_service = thriftpy2.load("./thrifts/chat_service.thrift", module_name="chat_thrift")

server = make_server(chat_service.ChatService, ChatServiceHandler(), "127.0.0.1", 9000)
server.serve()
