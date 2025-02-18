import grpc
import time
from concurrent import futures
import ai_pb2 as pb2
import ai_pb2_grpc as pb2_grpc
import json

from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from RAGFusion import RAGFusion

rag_fusion = RAGFusion(chat_llm=chat_llm,
                        tool_llm=tool_llm,
                        embeddings=embeddings,
                        vector_storage_dir=conf.storage_dir.vector,
                        top_k=conf.top_k)

class ChatServiceHandler(pb2_grpc.AIAgentServicer):
    def Single(self,request,context):
        answer=rag_fusion.query(request.question)
        return pb2.ChatResponse(answer=answer,end_of_stream=True)
    
    def StreamChat(self, request, context):
        try:
            messages=[{"role":msg.role,"content":msg.content}for msg in request.messages]
            for part_answer in rag_fusion.query(messages):
                yield pb2.ChatResponse(answer=part_answer,end_of_stream=False)
                time.sleep(0.1)
            yield pb2.ChatResponse(answer='[Done]',end_of_stream=True)
        except json.JSONDecodeError:
            yield pb2.ChatResponse(answer='Error: Invalid JSON format.',end_of_stream=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_AIAgentServicer_to_server(ChatServiceHandler(), server)
    server.add_insecure_port('127.0.0.1:5000')
    server.start()
    print("gRPC server is running on port 127.0.0.1:5000...")
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()