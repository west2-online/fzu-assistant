from typing import TypedDict, Optional, List
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter
import yaml
from utils import AmbiguityLevel, QuestionCompleter
from graph_store import GraphStore
from vector_store import VectorStore
from llms import chat_llm, tool_llm
from embeddings import embeddings

graph_store = GraphStore(llm=tool_llm)
vector_store = VectorStore(embeddings=embeddings)


class State(TypedDict):
    user_question: str
    vector_results: Optional[List[str]]
    graph_results: Optional[List[str]]
    response: Optional[str]



def start_parallel_queries(state: State, writer: StreamWriter) -> State:
    """并行查询入口"""
    # with ThreadPoolExecutor(max_workers=2) as t:
    #     tasks = [t.submit(vector_store.query, state["user_question"]),
    #              t.submit(graph_store.query, state["user_question"])]
    #     # tasks = [t.submit(vector_store.query, state["user_question"]),
    #     #          t.submit(graph_store.query, state["user_question"])]
    #     state["vector_results"] = tasks[0].result()
    #     state["graph_results"] = tasks[1].result().get("result")
    state["vector_results"] = yaml.dump([doc.page_content for doc in vector_store.query(state["user_question"])], allow_unicode=True)
    writer(state["vector_results"])
    state["graph_results"] = yaml.dump(graph_store.query(state["user_question"]), allow_unicode=True)
    writer(state["graph_results"])
    return state


def format_response(state: State, writer: StreamWriter) -> State:
    prompt = f"""
    用户的问题是：{state["user_question"]}
    请根据用户的问题，并且综合以下系统的结构化与非结构化数据源的信息，生成全面、准确的回答。
    请注意，如果你不确定答案的时候，请告诉用户通过查询得到答案。
    请格外注意，如果涉及学校政策（如：保研，新生入学安排等），不可直接回答，在已知相关政策链接的情况下推荐链接，不知道链接的情况下告诉用户可以查询福州大学教务处官网。
    【向量数据库检索结果】
    {state["vector_results"]}
    【图数据库检索结果】
    {state["graph_results"]}
    """
    # state["response"] = chat_llm.invoke(prompt)
    write = False
    state["response"] = ""
    for chunk in chat_llm.stream(prompt):
        content = chunk.content
        if content:
            state["response"] += content
            if write:
                writer(content)
            if "<｜Assistant｜>" in state["response"]:
                write = True
                state["response"] = state["response"].split("<｜Assistant｜>")[1]
                writer(state["response"])
    return state


# 构建流程图
builder = StateGraph(State)

# 添加节点
builder.add_node("start_parallel_queries", start_parallel_queries)

builder.add_node("format_response", format_response)

# 设置初始节点
builder.set_entry_point("start_parallel_queries")


# 设置并行分支（同时触发两个查询）
builder.add_edge("start_parallel_queries", "format_response")

# 设置结束节点
builder.add_edge("format_response", END)

# 编译流程图
graph = builder.compile()


import time
start = time.time()
state = State(user_question="福州大学有哪些校区？")

# chunk = ""
for chunk in graph.stream(state, stream_mode="custom"):
    print(chunk)
else:
    print(type(chunk), chunk)
print("time:", time.time()-start)
