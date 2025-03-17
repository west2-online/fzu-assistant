from NaiveRAG import NaiveRAG
from guardrails import Guard, OnFailAction, settings
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from guardrails.validator_base import (
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator
)
from utils import InputFilter, OuputFilter, HallucinationFilter

@register_validator(name="input check", data_type = "string")
class InputChecker(Validator):
    def __init__(self, tool_llm, on_fail = None, **kwargs):
        super().__init__(on_fail, **kwargs)
        self.filter = InputFilter(tool_llm)
    def _validate(self, value, metadata) -> ValidationResult:
        if self.filter(value):
            return FailResult(
                error_message="Input Invalid",
                fix_value = "输入含受限内容，请检查后重新输入。"
            )
        return PassResult()

@register_validator(name="output check", data_type = "string")
class OutputChecker(Validator):
    def __init__(self, tool_llm, on_fail = None, **kwargs):
        super().__init__(on_fail, **kwargs)
        self.filter = OuputFilter(tool_llm)
    def _validate(self, value, metadata) -> ValidationResult:
        filter_value = self.filter(value)
        if(filter_value == 0):
            return FailResult(
                error_message="Output Invalid",
                fix_value = "输出含受限内容，已终止输出。"
            )
        if(filter_value == 1):
            return PassResult(value_override = "(以下内容与福州大学无关，无法保证其正确性，请谨慎甄别)" + value)
        return PassResult()

@register_validator(name="hallucination check", data_type = "string")
class HallucinationsChecker(Validator):
    def __init__(self, tool_llm, on_fail = None, **kwargs):
        super().__init__(on_fail, **kwargs)
        self.filter = HallucinationFilter(tool_llm)
    
    def _validate(self, value, metadata):
        filter_value = self.filter(value, metadata['source'])
        if(filter_value == 1 or filter_value == 3):
            return FailResult(
                error_message = "Hallucination",
                fix_value = "大语言模型产生幻觉，终止输出。"
            )
        return PassResult()

class GuardrailsRAG:

    def __init__(self):
        self.last_vector_res = ""
        self.naive_rag = NaiveRAG(chat_llm=chat_llm,
                                tool_llm=tool_llm,
                                embeddings=embeddings,
                                vector_storage_dir=conf.storage_dir.vector,
                                top_k=conf.top_k)
        self.input_guard = Guard().use(
            InputChecker(tool_llm = tool_llm,on_fail = OnFailAction.FIX),
            on = "messages"
        )
        self.output_guard = Guard().use_many(
            OutputChecker(tool_llm = tool_llm, on_fail = OnFailAction.FIX),
            HallucinationsChecker(tool_llm = tool_llm, on_fail = OnFailAction.FIX)
        )

    def RAG(
        self,
        **kwargs
    ) -> str:
        
        """Custom LLM API wrapper"""
        
        message = kwargs.pop(message, [])
        query = message[-1]['content']
        history = message[:-1]

        result = self.naive_rag.query(query, history)
        self.last_vector_res = result.get("vector_results")

        return result.get("response")

    def query(self, query:str, history) -> str:
        if(history is None):
            history = []
        history.append({"roles": "user", "content": query})
        result = self.input_guard(
            self.RAG,
            messages = history
        )
        if len(self.last_vector_res) > 10:
            result = self.output_guard.parse(
                llm_output = result.validated_output,
                metadata={"source":self.last_vector_res}
            )
        return result.validated_output

if __name__ == '__main__':
    rag = GuardrailsRAG()
    GuardrailsRAG().on_call("福州大学的校训是什么？")