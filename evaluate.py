import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from deepeval.models import DeepEvalBaseLLM
from config import conf


class Deepseek_R1_7B(DeepEvalBaseLLM):
    def __init__(self):
        model_id = conf.chat_llm
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(model_id)
        self.pipe = pipeline(
            "text-generation", 
            model=self.model, 
            tokenizer=self.tokenizer, 
            max_new_tokens=4096
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        # result = self.pipe(prompt)
        result = self.model.invoke(prompt)
        return result

    async def a_generate(self, prompt: str) -> str:
        return self.generate(prompt)

    def get_model_name(self):
        return "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    

ds = Deepseek_R1_7B()
res = ds.generate("你好？")
print(res)
