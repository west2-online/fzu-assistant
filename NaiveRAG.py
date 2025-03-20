import typing as t
import yaml
import time
from utils.question_completer import QuestionCompleter
from utils import reciprocal_rank_fusion
from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter

from vector_store import VectorStore


class State(t.TypedDict):
    origin_query: str
    similar_queries: t.Optional[t.List[str]]
    vector_results: t.Optional[t.List[str]]
    response: t.Optional[str]
    history: t.List[str]
    token_usage: int


class NaiveRAG:
    def __init__(self, tool_llm, chat_llm, embeddings, vector_storage_dir, top_k):
        self.tool_llm = tool_llm
        self.chat_llm = chat_llm
        self.vector_store = VectorStore(embeddings=embeddings, 
                                storage_dir=vector_storage_dir,
                                top_k=top_k)
        self.question_completer = QuestionCompleter(self.tool_llm)
        graph_builder = (StateGraph(State)
        .add_node("retrieval", self.retrieval)
        .add_node("format_response", self.format_response)
        .set_entry_point("retrieval")
        .add_edge("retrieval", "format_response")
        .add_edge("format_response", END))

        self.graph = graph_builder.compile()

    def retrieval(self, state: State, writer: StreamWriter) -> State: 
        result = reciprocal_rank_fusion([
            self.vector_store.query(query) for query in [state["origin_query"]] + self.question_completer(state["origin_query"])
        ])
        state["vector_results"] = yaml.dump([doc.page_content for doc in result], allow_unicode=True)
        # writer(state["vector_results"])
        return state

    def format_response(self, state: State, writer: StreamWriter) -> State:
        prompt = f"""
        你叫做福uu助手，是福州大学西二在线工作室成员实现的问答机器人。
        用户的问题是：{state["origin_query"]}
        请根据用户的问题，做出如下两点的判断：
        第一，如果用户的问题是问候、闲聊，与学生、校园、无关，请不要使用检索内容进行回答。
        第二，如果用户的问题与福州大学相关，综合以下系统的搜索出的数据源的信息回答。
        请格外注意，如果涉及学校通知或者政策，请将相关链接告知用户。
        ______【数据库检索结果】______
        {state["vector_results"]}
        """
        # print(state["vector_results"])
        state["history"] = state["history"].copy()
        state["history"].append({
            "role": "user",
            "content": prompt
        })

        state["response"] = None
                
        for chunk in self.chat_llm.stream(state["history"], stream_usage=True):
            writer(chunk)
            state["response"] = chunk if state["response"] is None else state["response"] + chunk
        writer(state)
        return state
    
    def command_chat(self):
        history = []
        total_token = []
        print("\033[46m'输入'exit'退出\033[0m")
        
        while (question:=input("\033[36m输入：\033[0m")) != "exit":
            start = time.perf_counter()
            print("\033[36m输出：\033[0m")
            whole_answer = ""
            
            state = State(origin_query=question, history=history)
            for chunk in self.graph.stream(state, stream_mode="custom"):
                if hasattr(chunk, "content"):
                    print(chunk.content, end="")
                    whole_answer += chunk.content
            else:
                print()
            # print(chunk)
            # print(chunk["response"].usage_metadata["total_tokens"])
            total_token.append(chunk["response"].usage_metadata["total_tokens"])
            history.append({
                "role": "user",
                "content": question
            })
            history.append({
                "role": "assistant",
                "content": whole_answer
            })
            print(f"\033[36m耗时：\033[0m{time.perf_counter()-start}")
            print(f"\033[36mtoken统计：\033[0m{total_token}")
            # print("全文：", whole_answer)
            # print("message", history)

    def query(self, query: str, history: t.Optional[t.List] = None):
        if history is None:
            history = []
        state = State(origin_query=query, history=history)
        result = self.graph.invoke(state)
        return result
    
    def stream(self, query, history):
        state = State(origin_query=query, history=history)
        for chunk in self.graph.stream(state, stream_mode="custom"):
                yield chunk


if __name__ == "__main__":
    from llms.vllm_llm import llm
    from embeddings import embeddings
    from config import conf
    naive_rag = NaiveRAG(chat_llm=llm,
                           tool_llm=llm,
                           embeddings=embeddings,
                           vector_storage_dir=conf.storage_dir.vector,
                           top_k=conf.top_k)
    naive_rag.command_chat()
    # print(naive_rag.query("达芬奇的生平是如何的").get("response"))你这个贱货，天生就是被人干的命，别浪费时间了！