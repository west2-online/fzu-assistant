import grpc
import time
import etcd3
import signal
import sys
import threading
from concurrent import futures
import ai_pb2 as pb2
import ai_pb2_grpc as pb2_grpc
import json
import logging

from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from RAGFusion import RAGFusion

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# 连接 etcd
etcd = etcd3.client(host='127.0.0.1', port=2379)
GRPC_SERVER_ADDRESS = "127.0.0.1:5000"
ETCD_SERVICE_KEY = f"/services/ai_agent/{GRPC_SERVER_ADDRESS}"

lease = etcd.lease(60)

rag_fusion = RAGFusion(chat_llm=chat_llm,
                        tool_llm=tool_llm,
                        embeddings=embeddings,
                        vector_storage_dir=conf.storage_dir.vector,
                        top_k=conf.top_k)

class ChatServiceHandler(pb2_grpc.AIAgentServicer):

    def StreamChat(self, request, context):
        """ 处理流式请求 """
        try:
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]

            if not messages or not isinstance(messages, list):
                logging.warning("StreamChat 收到无效的 messages 数据")
                yield pb2.ChatResponse(answer="错误：消息格式不正确", end_of_stream=True)
                return

            logging.info(f"StreamChat 请求: {messages[-1]}")

            start_time = time.time()
            for part_answer in rag_fusion.query(messages):
                if time.time() - start_time > 30:
                    logging.warning("StreamChat 超时，提前终止")
                    yield pb2.ChatResponse(answer="[Timeout] 请求超时", end_of_stream=True)
                    return

                yield pb2.ChatResponse(answer=part_answer, end_of_stream=False)
                time.sleep(0.1)

            yield pb2.ChatResponse(answer='[Done]', end_of_stream=True)

        except json.JSONDecodeError:
            logging.error("JSON 解析失败")
            yield pb2.ChatResponse(answer="错误：JSON 格式无效", end_of_stream=True)

        except Exception as e:
            logging.error(f"StreamChat 出错: {str(e)}")
            yield pb2.ChatResponse(answer="服务器内部错误，请稍后再试", end_of_stream=True)

def register_service():
    """ 向 etcd 注册 gRPC 服务 """
    logging.info(f"注册 gRPC 服务到 etcd: {ETCD_SERVICE_KEY}")
    etcd.put(ETCD_SERVICE_KEY, GRPC_SERVER_ADDRESS, lease=etcd.lease(60))  # 注册 60 秒过期

def keep_alive():
    """ 定期续约，防止 etcd 自动删除服务 """
    while True:
        try:
            lease.refresh()  # 续约，让 etcd 继续存储 gRPC 服务器地址
            logging.info("续约成功，服务仍然在线")
            time.sleep(30)  # 每 30 秒续约一次（比 60 秒的租约时间短一点）
        except Exception as e:
            logging.error(f"续约失败: {e}")

def unregister_service():
    """ 从 etcd 移除 gRPC 服务 """
    logging.info(f"从 etcd 注销 gRPC 服务: {ETCD_SERVICE_KEY}")
    etcd.delete(ETCD_SERVICE_KEY)

def handle_exit(sig, frame):
    """ 处理退出信号 """
    unregister_service()
    sys.exit(0)

def serve():
    """ 启动 gRPC 服务器，并注册到 etcd """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    pb2_grpc.add_AIAgentServicer_to_server(ChatServiceHandler(), server)
    server.add_insecure_port(GRPC_SERVER_ADDRESS)
    server.start()
    register_service()

    threading.Thread(target=keep_alive, daemon=True).start()

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    logging.info(f"gRPC server is running on {GRPC_SERVER_ADDRESS}...")
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()
    