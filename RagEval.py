import os
import json
import random
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_recall, context_precision
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from RAGFusion import RAGFusion
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from tqdm import tqdm
os.environ["ZHIPUAI_API_KEY"] = "e0f73a83c7224e93bb3d8e1212e66ba1.sFOEqa2KcHNZIk0B"

def initialize_zhipuai_models():
    zhipu_chat = ChatZhipuAI(model='glm-4-Air')
    zhipu_embedding = ZhipuAIEmbeddings(model="embedding-3")
    return LangchainLLMWrapper(zhipu_chat), LangchainEmbeddingsWrapper(zhipu_embedding)

def generate_test_results():
    # 读取数据
    qa_data, link_data = [], []
    data_dir = "data"
    for root, _, files in os.walk(data_dir):
        for filename in files:
            if filename.endswith(".json"):
                with open(os.path.join(root, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        if "question" in data[0]:
                            qa_data.extend(data)
                        elif "title" in data[0]:
                            link_data.extend(data)
    
    # 划分测试集
    random.shuffle(qa_data)
    random.shuffle(link_data)
    split_qa = int(0.9 * len(qa_data))
    split_link = int(0.9 * len(link_data))
    test_set = qa_data[split_qa:] + link_data[split_link:]
    random.shuffle(test_set)
    test_set = test_set[:500]
    
    # 初始化 RAGFusion
    rag_fusion = RAGFusion(
        chat_llm=chat_llm,
        tool_llm=tool_llm,
        embeddings=embeddings,
        vector_storage_dir=conf.storage_dir.vector,
        top_k=conf.top_k,
    )
    
    # 生成测试结果
    test_results = []
    for sample in tqdm(test_set):
        if "question" in sample:
            question = sample["question"]
            reference = sample["answer"]
            model_answer = rag_fusion.query(question)
            contexts = rag_fusion.vector_store.query(question)
            contexts = [doc.page_content for doc in contexts]
        else:
            question = sample["title"]
            reference = sample["link"]
            model_answer = rag_fusion.query(question)
            contexts = [sample["link"]]
        test_results.append({
            "question": question,
            "answer": model_answer,
            "contexts": contexts,
            "reference": reference
        })
    
    # 保存测试结果
    with open("./eval_data/test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    return test_results

def main():
    # 初始化 LLM 和 Embeddings
    zhipu_llm, zhipu_embeddings = initialize_zhipuai_models()
    
    # test_results = generate_test_results()  # 第一次需要生成

    # 从 test_results.json 读取测试数据
    with open("./eval_data/test_results.json", "r", encoding="utf-8") as f:
        test_results = json.load(f)
    
    # 构造 RAGAS 评估数据
    df = pd.DataFrame(test_results)
    evalsets = Dataset.from_list(df.apply(lambda row: {
        "user_input": row["question"],
        "reference": row["reference"],
        "query": row["question"],
        "answer": row["answer"],
        "retrieved_contexts": row["contexts"]
    }, axis=1).tolist())
    
    # 配置评估指标
    faithfulness.llm = zhipu_llm
    answer_relevancy.llm = zhipu_llm
    answer_relevancy.embeddings = zhipu_embeddings
    context_recall.llm = zhipu_llm
    context_precision.llm = zhipu_llm
    
    # 运行评估
    result = evaluate(evalsets, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    result_df = result.to_pandas()
    
    # 计算四个指标的平均值
    avg_faithfulness = result_df["faithfulness"].mean()
    avg_answer_relevancy = result_df["answer_relevancy"].mean()
    avg_context_precision = result_df["context_precision"].mean()
    avg_context_recall = result_df["context_recall"].mean()
    
    print(f"Faithfulness 平均值: {avg_faithfulness:.4f}")
    print(f"Answer Relevancy 平均值: {avg_answer_relevancy:.4f}")
    print(f"Context Precision 平均值: {avg_context_precision:.4f}")
    print(f"Context Recall 平均值: {avg_context_recall:.4f}")

if __name__ == "__main__":
    main()
