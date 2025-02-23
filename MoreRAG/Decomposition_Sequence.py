import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import typing as t
import yaml
import time
from langgraph.graph import StateGraph, END
from langgraph.types import StreamWriter
from utils import SubProblemGenerator, Rerank, SubProblemSolver, InputFilter
from vector_store import VectorStore
from langchain_core.documents import Document


class State(t.TypedDict):
    origin_query: str
    sub_problems: t.Optional[t.List[str]]
    vector_results: t.Optional[t.List[str]]
    response: t.Optional[str]
    history: t.List[str]


class DecompositionSequence:
    def __init__(self, tool_llm, chat_llm, embeddings, vector_storage_dir, top_k, rerank_model = None):
        self.tool_llm = tool_llm
        self.chat_llm = chat_llm
        self.vector_store = VectorStore(embeddings=embeddings, 
                                        storage_dir=vector_storage_dir,
                                        top_k=top_k)
        self.sub_problem_generator = SubProblemGenerator(llm = tool_llm, isSequence = True)
        if(rerank_model is not None):
            self.rerank_model = Rerank(model = rerank_model)
        else:
            self.rerank_model = None
        self.sub_problem_solver = SubProblemSolver(llm = tool_llm, rerank = self.rerank_model)
        self.input_filter = InputFilter(tool_llm = tool_llm)
        
        graph_builder = (StateGraph(State)
                         .add_node("generate_sub_problems", self.generate_sub_problems)
                         .add_node("solve_sub_problems", self.solve_sub_problems)
                         .add_node("format_response", self.format_response)
                         .set_entry_point("generate_sub_problems")
                         .add_edge("generate_sub_problems", "solve_sub_problems")
                         .add_edge("solve_sub_problems", "format_response")
                         .add_edge("format_response", END))

        self.graph = graph_builder.compile()

    def generate_sub_problems(self, state: State, writer: StreamWriter) -> State:
        state["sub_problems"] = self.sub_problem_generator(state["origin_query"])
        return state

    def solve_sub_problems(self, state: State, writer: StreamWriter) -> State:
        last_answer = ""
        for sub_problem in state["sub_problems"]:
            ans = self.sub_problem_solver(sub_problem, last_answer, self.vector_store)
            last_answer = ans
        res = self.vector_store.query(state['origin_query'])
        res.append(Document(
            page_content = last_answer
        ))
        if(self.rerank_model is not None):
            res = self.rerank_model(state['origin_query'], res)
        state['vector_results'] = yaml.dump([doc.page_content for doc in res], allow_unicode=True)
        return state

    def format_response(self, state: State, writer: StreamWriter) -> State:
        prompt = f"""
        用户的问题是：{state["origin_query"]}
        请根据用户的问题，并且综合以下系统的搜索出的数据源的信息，不要做过多描述。
        请格外注意，如果涉及学校通知或者政策（如：保研，新生入学安排等），请直接将相关通知或政策的链接告知用户。
        如果提供的信息与用户提出的问题无关，且你并不知道这个问题的准确回答，直接向用户说明你不知道。
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
                pass
            print(f"测试问题：{question} 耗时：{time.perf_counter()-start}")

    def command_chat(self):
        history = []
        total_token = 0
        print("\033[46m'输入'exit'退出\033[0m")
        while (question := input("\033[36m输入：\033[0m")) != "exit":
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
        if(self.input_filter(query)):
            return {
                "response": "输入内容包含受限信息，请调整表述后重新提交。",
                "retrieved_docs": ""
            }
        if history is None:
            history = []
        state = State(origin_query=query, history=history)
        result = self.graph.invoke(state)
        return {
            "response": result.get("response"),
            "retrieved_docs": yaml.safe_load(result.get("vector_results", "[]"))  # 解析 YAML
        }


if __name__ == "__main__":
    from llms import chat_llm, tool_llm
    from embeddings import embeddings
    from config import conf
    from utils import rrk_model
    decomposition_sequence = DecompositionSequence(chat_llm=chat_llm,
                                                  tool_llm=tool_llm,
                                                  embeddings=embeddings,
                                                  vector_storage_dir=conf.storage_dir.vector,
                                                  top_k=conf.top_k,
                                                  rerank_model= rrk_model)
    decomposition_sequence.command_chat()
