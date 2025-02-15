from typing import TypedDict, Optional, List
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter
import yaml
import time
from utils import VectorStore, GraphStore, QueryGenerator, reciprocal_rank_fusion
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf


class State(TypedDict):
    origin_query: str
    similar_queries: Optional[List[str]]
    vector_results: Optional[List[str]]
    graph_results: Optional[List[str]]
    response: Optional[str]


graph_store = GraphStore(llm=tool_llm, 
                         url=conf.neo4j.url,
                         username=conf.neo4j.username,
                         password=conf.neo4j.password)
vector_store = VectorStore(embeddings=embeddings, 
                           storage_dir=conf.storage_dir.notice, 
                           top_k=conf.top_k)
query_generator = QueryGenerator(llm=tool_llm)


def generate_similar_queries(state: State, writer: StreamWriter) -> State:
    state["similar_queries"] = query_generator(state["origin_query"])
    writer(state["similar_queries"])
    return state

def retrieval(state: State, writer: StreamWriter) -> State:    
    result = [
        vector_store.query(query) for query in [state["origin_query"]] + state["similar_queries"]
    ]
    reranked_result = reciprocal_rank_fusion(result)
    state["vector_results"] = yaml.dump([doc.page_content for doc in reranked_result], allow_unicode=True)
    # writer(state["vector_results"])
    state["graph_results"] = []
    state["graph_results"] = yaml.dump(graph_store.query(state["origin_query"]), allow_unicode=True)
    # writer(state["graph_results"])
    return state


def format_response(state: State, writer: StreamWriter) -> State:
    prompt = f"""
    用户的问题是：{state["origin_query"]}
    请根据用户的问题，并且综合以下系统的搜索出的数据源的信息，不要做过多描述。
    请格外注意，如果涉及学校通知或者政策（如：保研，新生入学安排等），请直接将相关通知或政策的链接告知用户
    【向量数据库检索结果】
    {state["vector_results"]}
    【图数据库检索结果】
    {state["graph_results"]}
    """
    writer(prompt)
    state["response"] = chat_llm.invoke(prompt).content
    writer(state["response"])

    # write = False
    # for chunk in chat_llm.stream(prompt):
    #     content = chunk.content
    #     if content:
    #         state["response"] += content
    #         if write:
    #             writer(content)
    #         if "<｜Assistant｜>" in state["response"]:
    #             write = True
    #             state["response"] = state["response"].split("<｜Assistant｜>")[1]
    #             writer(state["response"])
    return state

                                                     
builder = (StateGraph(State).add_node("generate_similar_queries", generate_similar_queries)
 .add_node("retrieval", retrieval)
 .add_node("format_response", format_response)
 .set_entry_point("generate_similar_queries")
 .add_edge("generate_similar_queries", "retrieval")
 .add_edge("retrieval", "format_response")
 .add_edge("format_response", END))

graph = builder.compile()

question = "校友入校要申请什么？"
while True:
    if question == "exit":
        break
    state = State(origin_query=question)
    start = time.perf_counter()
    for chunk in graph.stream(state, stream_mode="custom"):
        print(chunk, end="")
        pass
    print("time:", time.perf_counter()-start)
    question = input("输入：")
