import thriftpy2

chat_service = thriftpy2.load("./thrifts/chat_service.thrift", module_name="chat_thrift")

from thriftpy2.rpc import make_client

client = make_client(chat_service.ChatService, "127.0.0.1", 9000)

msg = client.chat("福州大学的校训是什么？")
print(msg)