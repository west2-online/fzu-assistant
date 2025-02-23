import grpc
import ai_pb2 as pb2
import ai_pb2_grpc as pb2_grpc

def run_streaming_request():
    """ 流式请求客户端 """
    channel = grpc.insecure_channel('127.0.0.1:5000')
    stub = pb2_grpc.AIAgentStub(channel)

    # 创建多个消息（模拟一个完整的对话）
    messages = [
        pb2.Message(role="system", content="你是一个AI助手，帮助用户回答问题。"),
        pb2.Message(role="user", content="你好，请帮我解决一些问题。"),
        pb2.Message(role="assistant", content="当然可以，请告诉我你的问题。"),
        pb2.Message(role="user", content="请告诉我福州大学的基本信息。")
    ]

    # 创建 ChatRequest，传入这些消息
    request = pb2.ChatRequest(message=messages)

    # 调用 StreamChat，接收流式响应
    response_iterator = stub.StreamChat(request)

    # 打印每个返回的响应
    for response in response_iterator:
        print(f"{response.answer}", flush=True ,end='')


if __name__ == '__main__':
    run_streaming_request()
