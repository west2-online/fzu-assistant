import os
import json
import time
import random
from langchain_community.document_loaders import JSONLoader
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.testset import TestsetGenerator

# 设置 API Key
os.environ["ZHIPUAI_API_KEY"] = "7ec63d7bedf748ba8bfdc2715a3bb534.6sD9B4RFA1Jzjx9t"

# 初始化 ZhipuAI 模型
def initialize_zhipuai_models():
    zhipu_chat = ChatZhipuAI(model='glm-4-Air')
    zhipu_embedding = ZhipuAIEmbeddings(model="embedding-3")
    zhipu_llm = LangchainLLMWrapper(zhipu_chat)
    zhipu_embeddings = LangchainEmbeddingsWrapper(zhipu_embedding)
    return zhipu_llm, zhipu_embeddings

def generate_testset():
    directories = ["./data/QA", "./data/notice"]
    all_docs = []
    
    for directory in directories:
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".json"):
                    json_path = os.path.join(root, file)
                    print(f"正在处理: {json_path}")

                    loader = JSONLoader(file_path=json_path, jq_schema=".", text_content=False)
                    docs = loader.load()
                    
                    for doc in docs:
                        doc.page_content = doc.page_content.encode().decode('unicode_escape')
                    
                    all_docs.extend(docs)
    
    random.shuffle(all_docs)
    all_docs = all_docs[:3]
    generator_llm, generator_embeddings = initialize_zhipuai_models()
    generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
    dataset = generator.generate_with_langchain_docs(all_docs, testset_size=10)
    
    df = dataset.to_pandas()
    testset_path = "./eval/eval_data/testset.json"
    df.to_json(testset_path, orient="records", force_ascii=False)
    print(f"测试集已保存为 {testset_path}")
    translate_testset(testset_path)

def translate_testset(file_path):
    llm = ChatZhipuAI(model='glm-4-Air')
    
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    def translate_text(text):
        if not text.strip():
            return text
        
        prompt = f"请将以下英文翻译成简体中文：\n\n{text}"
        while True:
            try:
                response = llm.invoke(prompt)
                return response.content.strip()
            except Exception as e:
                if "429 Too Many Requests" in str(e):
                    print("请求过载，等待 5 秒重试...")
                    time.sleep(5)
                else:
                    print("翻译失败:", e)
                    return text

    for d in data:
        if "user_input" in d:
            d["user_input"] = translate_text(d["user_input"])
        if "reference" in d:
            d["reference"] = translate_text(d["reference"])

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"翻译完成，已更新 {file_path} 文件！")

if __name__ == '__main__':
    testset_path = generate_testset()
