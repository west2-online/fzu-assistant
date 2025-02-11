from typing import TypedDict, Optional, List
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED, ALL_COMPLETED
from langgraph.graph import StateGraph, END
from utils import AmbiguityLevel, QuestionCompleter, DataLoader
from graph_store import GraphStore
from vector_store import VectorStore
from llms import chat_llm, tool_llm
from embeddings import embeddings


ambiguity_level = AmbiguityLevel(llm=tool_llm)
question_completer = QuestionCompleter(llm=tool_llm)


class State(TypedDict):
    user_question: str
    ambiguity_level: Optional[str]
    vector_results: Optional[List[str]]
    graph_results: Optional[List[str]]
    web_results: Optional[List[str]]
    combined_results: Optional[str]
    response: Optional[str]


def assess_ambiguity(state: State) -> State:
    """判断问题模糊程度"""
    level_action_map = {
        3: "clarify_question",
        2: "direct_query",
        1: "direct_query"
    }
    level = ambiguity_level(state["user_question"])
    state["ambiguity_level"] = level_action_map[level]
    print(state)
    return state


def clarify_question(state: State) -> State:
    """追问更多信息"""
    # 这里添加实际追问逻辑
    state["response"] = question_completer(question=state["user_question"])
    return state


def start_parallel_queries(state: State) -> State:
    """并行查询入口"""
    with ThreadPoolExecutor(max_workers=2) as t:
        tasks = [t.submit(vector_store.query, state["user_question"]),
                 t.submit(graph_store.query, state["user_question"])]
        # tasks = [t.submit(vector_store.query, state["user_question"]),
        #          t.submit(graph_store.query, state["user_question"])]
        state["vector_results"] = tasks[0].result()
        state["graph_results"] = tasks[1].result().get("result")
    return state


def format_response(state: State) -> State:
    prompt = f"""
    用户的问题是：{state["user_question"]}
    请根据用户的问题，并且综合以下来自结构化与非结构化数据源的信息，生成全面、准确且连贯的回答：
    【向量数据库检索结果】
    {[doc.page_content for doc in state["vector_results"]]}
    【图数据库检索结果】
    {state["graph_results"]}
    """
    state["response"] = chat_llm.invoke(prompt)
    return state


# 构建流程图
builder = StateGraph(State)

# 添加节点
builder.add_node("assess_ambiguity", assess_ambiguity)

builder.add_node("clarify_question", clarify_question)
builder.add_node("start_parallel_queries", start_parallel_queries)

builder.add_node("format_response", format_response)

# 设置初始节点
builder.set_entry_point("assess_ambiguity")

# 添加条件分支
builder.add_conditional_edges(
    "assess_ambiguity",
    lambda state: state["ambiguity_level"],
    {
        "clarify_question": "clarify_question",
        "direct_query": "start_parallel_queries"  # 改为指向并行入口
    }
)
# 添加追问循环
builder.add_edge("clarify_question", END)

# 设置并行分支（同时触发两个查询）
builder.add_edge("start_parallel_queries", "format_response")

# 设置结束节点
builder.add_edge("format_response", END)

# 编译流程图
graph = builder.compile()


import time
start = time.time()
state = State(user_question="福州大学有哪些校区？")
result = graph.invoke(state)
print("time:", time.time()-start)
resp = result.get("response")
print(resp)

