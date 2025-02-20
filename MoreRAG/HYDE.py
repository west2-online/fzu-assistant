import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import typing as t
import yaml
import time

from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter

from utils import PassageGenerator, reciprocal_rank_fusion
from vector_store import VectorStore


class State(t.TypedDict):
    origin_query: str
    passage: t.Optional[t.List[str]]
    vector_results: t.Optional[t.List[str]]
    response: t.Optional[str]
    history: t.List[str]


class HYDE:
    def __init__(self, tool_llm, chat_llm, embeddings, vector_storage_dir, top_k, rerank = None):
        self.tool_llm = tool_llm
        self.chat_llm = chat_llm
        self.vector_store = VectorStore(embeddings=embeddings, 
                                storage_dir=vector_storage_dir,
                                top_k=top_k)
        self.passage_generator = PassageGenerator(llm=tool_llm)
        self.rerank_model = rerank
        graph_builder = (StateGraph(State).add_node("generate_passage", self.generate_passage)
        .add_node("retrieval", self.retrieval)
        .add_node("format_response", self.format_response)
        .set_entry_point("generate_passage")
        .add_edge("generate_passage", "retrieval")
        .add_edge("retrieval", "format_response")
        .add_edge("format_response", END))

        self.graph = graph_builder.compile()

    def generate_passage(self, state: State, writer: StreamWriter) -> State:
        state["passage"] = self.passage_generator(state["origin_query"])
        # writer(state["passage"])
        return state

    def retrieval(self, state: State, writer: StreamWriter) -> State:    
        result = [
            self.vector_store.query(query) for query in [state["origin_query"], state["passage"]]
        ]
        reranked_result = reciprocal_rank_fusion(result)
        if(self.rerank_model is not None):
            reranked_result = self.rerank_model(state['origin_query'], reranked_result)
        state["vector_results"] = yaml.dump([doc.page_content for doc in reranked_result], allow_unicode=True)
        # writer(state["vector_results"])
        return state

    def format_response(self, state: State, writer: StreamWriter) -> State:
        prompt = f"""
        用户的问题是：{state["origin_query"]}
        请根据用户的问题，并且综合以下系统的搜索出的数据源的信息，不要做过多描述。
        请格外注意，如果涉及学校通知或者政策（如：保研，新生入学安排等），请直接将相关通知或政策的链接告知用户
        【向量数据库检索结果】
        {state["vector_results"]}
        """
        # writer(prompt)
        # state["response"] = chat_llm.invoke(prompt).content
        # writer(state["response"])

        state["response"] = ""
        for chunk in self.chat_llm.stream(prompt, history=state["history"]):
            content = chunk
            if content:
                state["response"] += content
                writer(content)
        return state
    
    def measure_speed(self, question="福州大学的校训是什么？"):
        for _ in range(10):
            state = State(origin_query=question)
            start = time.perf_counter()
            for chunk in self.graph.stream(state, stream_mode="custom"):
                # print(chunk, end="")
                pass
            print(f"测试问题：{question} 耗时：{time.perf_counter()-start}")
    
    def command_chat(self):
        history = []
        total_token = 0
        print("\033[46m'输入'exit'退出\033[0m")
        while (question:=input("\033[36m输入：\033[0m")) != "exit":
            start = time.perf_counter()
            print("\033[36m输出：\033[0m")
            whole_answer = ""
            state = State(origin_query=question, history=history)
            for chunk in self.graph.stream(state, stream_mode="custom"):
                print(chunk, end="")
                whole_answer += chunk
            print()
            print(f"\033[36m耗时：\033[0m{time.perf_counter()-start}")
            print(f"\033[36mtoken统计：\033[0m{total_token}")
            history.append({
                "role": "user",
                "content": question
            })
            history.append({
                "role": "assistant",
                "content": whole_answer
            })
            print(history)

    def query(self, query: str, history: t.Optional[t.List] = None):
        if history is None:
            history = []
        state = State(origin_query=query, history=history)
        return self.graph.invoke(state).get("response")
            

if __name__ == "__main__":
    from llms import chat_llm, tool_llm
    from embeddings import embeddings
    from config import conf
    from utils import rerank
    hyde = HYDE(chat_llm=chat_llm,
                           tool_llm=tool_llm,
                           embeddings=embeddings,
                           vector_storage_dir=conf.storage_dir.vector,
                           top_k=conf.top_k,
                           rerank=rerank)
    hyde.command_chat()
