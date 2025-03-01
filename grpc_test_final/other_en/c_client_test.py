import grpc
import ai_agent_pb2
import ai_agent_pb2_grpc

def build_messages():
    return [
        ai_agent_pb2.Message(role="system", content="你是一个AI助手，帮助用户回答问题。"),
        ai_agent_pb2.Message(role="user", content="请告诉我福州大学的基本信息。")
    ]

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = ai_agent_pb2_grpc.AIAgentStub(channel)

    # 构建请求
    request = ai_agent_pb2.ChatRequest(message=build_messages())

    try:
        for response in stub.StreamChat(request):
            print(response.answer, end='', flush=True)
            if response.end_of_stream:
                print("\n对话结束")

    except grpc.RpcError as e:
        print(f"\nRPC错误: {e.code()} - {e.details()}")

if __name__ == '__main__':
    run()
