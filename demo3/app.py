from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END


# 定义状态结构
class GraphState(TypedDict):
    user_question: str
    ambiguity_level: int
    clarified_question: Optional[str]
    vector_results: Optional[List[str]]
    graph_results: Optional[List[str]]
    web_results: Optional[List[str]]
    combined_results: Optional[List[str]]


def user_query(state: GraphState) -> GraphState:
    return state


# 定义节点函数
def assess_ambiguity(state: GraphState) -> GraphState:
    """判断问题模糊程度"""
    # 这里添加实际的模糊判断逻辑
    state["ambiguity_level"] = 2
    return state


def decide_to_ask(state: GraphState) -> str:
    # return "clarify_question"
    return "direct_query"


def clarify_question(state: GraphState) -> GraphState:
    """追问更多信息"""
    # 这里添加实际追问逻辑
    state["clarified_question"] = "用户补充后的提问"
    return state


def complete_question(state: GraphState) -> GraphState:
    """尝试补全问题"""
    # 这里添加问题补全逻辑
    state["clarified_question"] = "补全后的完整问题"
    return state


def start_parallel_queries(state: GraphState) -> GraphState:
    """并行查询入口（空操作仅用于流程控制）"""
    state["graph_results"] = ["图查询结果"]
    state["vector_results"] = ["向量查询结果"]
    return state


def aggregate_results(state: GraphState) -> GraphState:
    """汇聚查询结果"""
    if state.get("vector_results") and state.get("graph_results"):
        state["combined_results"] = state["vector_results"] + state["graph_results"]
    return state


def decide_web_search(state: GraphState) -> str:
    return "has_results" if state.get("combined_results") else "no_results"


def check_results(state: GraphState) -> GraphState:
    """检查查询结果"""
    return state


def web_search(state: GraphState) -> GraphState:
    """执行Web搜索"""
    # 这里添加实际搜索逻辑
    state["web_results"] = ["网络搜索结果"]
    return state


def format_response(state: GraphState) -> GraphState:
    return state


# 构建流程图
builder = StateGraph(GraphState)

# 添加节点
builder.add_node("user_query", user_query)
builder.add_node("assess_ambiguity", assess_ambiguity)

builder.add_node("clarify_question", clarify_question)
builder.add_node("complete_question", complete_question)
builder.add_node("start_parallel_queries", start_parallel_queries)

builder.add_node("aggregate_results", aggregate_results)
builder.add_node("check_results", check_results)
builder.add_node("web_search", web_search)
builder.add_node("format_response", format_response)

# 设置初始节点
builder.set_entry_point("user_query")

# 添加条件分支
builder.add_conditional_edges(
    "assess_ambiguity",
    decide_to_ask,
    {
        "clarify_question": "clarify_question",
        "complete_question": "complete_question",
        "direct_query": "start_parallel_queries"  # 改为指向并行入口
    }
)

builder.add_edge("user_query", "assess_ambiguity")
# 添加追问循环
builder.add_edge("clarify_question", "assess_ambiguity")

builder.add_edge("complete_question", "start_parallel_queries")

# 设置并行分支（同时触发两个查询）
builder.add_edge("start_parallel_queries", "aggregate_results")

# 结果处理流程
builder.add_edge("aggregate_results", "check_results")
builder.add_conditional_edges(
    "check_results",
    decide_web_search,
    {
        "has_results": "format_response",
        "no_results": "web_search"
    }
)
builder.add_edge("web_search", "format_response")

# 设置结束节点
builder.add_edge("format_response", END)

# 编译流程图
flow = builder.compile()

# 初始化状态
initial_state = GraphState(user_question="原始问题",
                           clarified_question=None,
                           vector_results=None,
                           graph_results=None,
                           web_results=None,
                           combined_results=None)

# 执行流程
for step in flow.stream(initial_state):
    print(f"当前状态：{step}")
