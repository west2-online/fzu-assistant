import grpc
from concurrent import futures
import etcd3
import time
import signal
import sys
import threading
import requests
import json
import ai_agent_pb2
import ai_agent_pb2_grpc
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

# 连接etcd
etcd = etcd3.client(host='127.0.0.1', port=2379)

# gRPC 服务器配置
GRPC_SERVER_ADDRESS = "[::]:50051"
ETCD_SERVICE_KEY = f"/services/ai_agent/{GRPC_SERVER_ADDRESS}"

lease = etcd.lease(60)

class AIAgentServicer(ai_agent_pb2_grpc.AIAgentServicer):

    def Single(self, request, context):
        pass
    
    def StreamChat(self, request, context):
        messages = [{"role": msg.role, "content": msg.content} for msg in request.message]

        # 调用外部 A 服务
        try:
            with requests.post(
                'http://localhost:5000/v1/chat/completions',
                json={'messages': messages},
                stream=True,
                timeout=120
            ) as r:
                for line in r.iter_lines():
                    if line:
                        data = json.loads(line)
                        yield ai_agent_pb2.ChatResponse(
                            answer=data.get('content', ''),
                            end_of_stream=data.get('completed', False)
                        )
        except Exception as e:
            yield ai_agent_pb2.ChatResponse(
                answer=f"服务错误: {str(e)}",
                end_of_stream=True
            )

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
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    ai_agent_pb2_grpc.add_AIAgentServicer_to_server(AIAgentServicer(), server)
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
