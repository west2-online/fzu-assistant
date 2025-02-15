import thriftpy2


class Min_Bar_ServiceHandler:
    def min_bar(self, id, context):
        return context + ", id" + str(id)
    
tf_service = thriftpy2.load("./thrifts/tf_service.thrift", module_name="tf_service_thrift")

from thriftpy2.rpc import make_server

server = make_server(tf_service.Min_Bar_Service, Min_Bar_ServiceHandler(), "127.0.0.1", 9000)
server.serve()