from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.outputs import GenerationChunk
from langchain_core.language_models.llms import LLM
from openai import OpenAI
import copy
import typing as t


class VLLMClient(LLM):
    api_key: str = "EMPTY"
    base_url: str = "http://localhost:8000/v1"

    def _call(self,
              prompts: t.List[str],
              stop: t.Optional[t.List[str]] = None,
              run_manager: t.Optional[CallbackManagerForLLMRun] = None,
              **kwargs: t.Any,
            )  -> str:
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        history = kwargs.get("history", None)
        message = {
            "role": "user",
            "content": prompts
        }
        if history is None:
            messages = []
            messages.append(message)
        else:
            messages = copy.copy(history)
        response = client.chat.completions.create(
            model=client.models.list().data[0].id,
            messages=messages
        )
        return response.choices[0].message.content

    def _stream(
            self,
            prompt: str,
            stop: t.Optional[t.List[str]] = None,
            run_manager: t.Optional[CallbackManagerForLLMRun] = None,
            **kwargs: t.Any,
        ) -> t.Iterator[GenerationChunk]:
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        history = kwargs.get("history", None)
        message = {
            "role": "user",
            "content": prompt
        }
        if history is None:
            messages = []
            messages.append(message)
        else:
            messages = copy.copy(history)
        response = client.chat.completions.create(
            model=client.models.list().data[0].id,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True}
        )
        for chunk in response:
            if isinstance(chunk.choices, list) and len(chunk.choices) == 0:
                total_token = chunk.usage.total_tokens
                return total_token
            else:
                content = chunk.choices[0].delta.content
                yield GenerationChunk(text=content)
    
    def command_chat(self):
        history = []
        print("\033[46m'输入'exit'退出\033[0m")
        while (question:=input("\033[36m输入：\033[0m")) != "exit":
            history.append({
                "role": "user",
                "content": question
            })
            whole_answer = ""
            try:
                print("\033[36m输出：\033[0m", end="")
                response = self.stream(question, history=history)
                while True:
                    answer = next(response)
                    print(answer, end="", flush=True)
                    whole_answer += answer
            except StopIteration as e:
                total_text_length = e.value
                print()
            history.append({
                "role": "assistant",
                "content": whole_answer
            })
        print(f"\033[36m消耗token:\033[0m {total_text_length}")
    
    @property
    def _llm_type(self):
        return "custom vllm client"


if __name__ == "__main__":
    llm = VLLMClient()
    # print(llm.invoke("你好"))
    llm.command_chat()
