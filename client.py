import thriftpy2

tf_service = thriftpy2.load("./thrifts/tf_service.thrift", module_name="tf_service_thrift")

from thriftpy2.rpc import make_client

client = make_client(tf_service.Min_Bar_Service, "127.0.0.1", 9000)

id = 42
context = "quququsb"
msg = client.min_bar(id, context)
print(msg)