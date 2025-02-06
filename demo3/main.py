from utils import DataLoader
from llms import zhipu
from embeddings import embeddings
from graph_store import GraphStore
from vector_store import VectorStore
from utils import AmbiguityLevel

# load data
# loader = DataLoader("./data")
# documents = loader.load_and_split()
# print(len(documents))
# print(documents)

# graph
# graph_store = GraphStore(llm=zhipu)
# graph_store.add_documents(documents)
# print(graph_store.query("福州大学有哪些校区？"))
# graph_result = graph_store.query("福州大学有哪些校区？").get("result", "")

# # vector
# vector_store = VectorStore(embeddings=embeddings)
# vector_store.add_documents(documents=documents)
# print(vector_store.query("福州大学有哪些校区？"))
# vector_result = [res.page_content for res in vector_store.query("福州大学有哪些校区？")]

# graph_result = {'result': [{'fzu': {'id': '福州大学'}, 'r': ({'id': '旗山校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '旗山校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '泉港校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '泉港校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '上杭校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '上杭校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '晋江校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '晋江校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '怡山校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '怡山校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '铜盘校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '铜盘校区'}}, {'fzu': {'id': '福州大学'}, 'r': ({'id': '集美校区'}, '属于', {'id': '福州大学'}), 'campus': {'id': '集美校区'}}]}
# vector_result = ["{'question': '福州大学有哪些校区？详细地址是什么', 'answer': '旗山校区、铜盘校区、晋江校区、怡山校区、泉港校区、集美校区、上杭校区。'}", "{'question': '福州大学有多少个学院和学生？', 'answer': '学校设有27个学院（含1个独立学院和1个中外合作办学学院）和1家附属省立医院。现有在校普通本科学生39578人（其中至诚学院学生13222人），各类博、硕士研究生18381人'}", "{'question': '福州大学的校训是什么？', 'answer': '福州大学的校训是“明德至诚，博学远志”'}"]

# ambiguity level
# ambiguity_level = AmbiguityLevel(zhipu)
# print(ambiguity_level("保研？"))  # 3
# print(ambiguity_level("关于食堂的事情？"))  # 2
# print(ambiguity_level("请告诉我2024年福州大学srtp的相关信息"))  # 1
