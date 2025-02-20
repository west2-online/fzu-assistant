import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
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
from NaiveRAG import NaiveRAG
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from tqdm import tqdm
from testset import generate_testset
from MoreRAG.Decomposition_Individual import DecompositionIndividual
from MoreRAG.Decomposition_Sequence import DecompositionSequence
from MoreRAG.HYDE import HYDE
from MoreRAG.StepBack import StepBack

# 设置 API Key
os.environ["ZHIPUAI_API_KEY"] = "7ec63d7bedf748ba8bfdc2715a3bb534.6sD9B4RFA1Jzjx9t"

# 初始化 ZhipuAI

def initialize_zhipuai_models():
    zhipu_chat = ChatZhipuAI(model='glm-4-Air')
    zhipu_embedding = ZhipuAIEmbeddings(model="embedding-3")
    return LangchainLLMWrapper(zhipu_chat), LangchainEmbeddingsWrapper(zhipu_embedding)

# 生成测试结果
def generate_test_results():
    if not os.path.exists("./eval/eval_data/testset.json"):
        print("未找到测试数据，正在生成...")
        generate_testset()
    
    with open("./eval/eval_data/testset.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # 初始化 RAGFusion
    rag_fusion = StepBack(
        chat_llm=chat_llm,
        tool_llm=tool_llm,
        embeddings=embeddings,
        vector_storage_dir=conf.storage_dir.vector,
        top_k=conf.top_k,
    )
    
    test_results = []
    for sample in tqdm(test_data, desc="Generating test results"):
        question = sample.get("user_input", "")
        reference = sample.get("reference", "")
        retrieved_contexts = sample.get("reference_contexts", [])
        model_answer = rag_fusion.query(question)  # 由 RAGFusion 生成答案
        
        test_results.append({
            "user_input": question,  # 添加 user_input 列
            "query": question,
            "reference": reference,
            "retrieved_contexts": retrieved_contexts,
            "answer": model_answer
        })
    
    os.makedirs("./eval/eval_data", exist_ok=True)
    with open("./eval/eval_data/answer_results.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    
    return test_results

# 评估主流程
def main():
    zhipu_llm, zhipu_embeddings = initialize_zhipuai_models()
    # if not os.path.exists("./eval/eval_data/answer_results.json"):
    test_results = generate_test_results()
    # else:
    #     with open("./eval/eval_data/answer_results.json", "r", encoding="utf-8") as f:
    #         test_results = json.load(f)
    # print(test_results)
    df = pd.DataFrame(test_results)
    evalsets = Dataset.from_list(df.to_dict(orient="records"))

    faithfulness.llm = zhipu_llm
    answer_relevancy.llm = zhipu_llm
    answer_relevancy.embeddings = zhipu_embeddings
    context_recall.llm = zhipu_llm
    context_precision.llm = zhipu_llm
    
    print("正在评估...")
    result = evaluate(evalsets, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    result_df = result.to_pandas()
    
    avg_faithfulness = result_df["faithfulness"].mean()
    avg_answer_relevancy = result_df["answer_relevancy"].mean()
    avg_context_precision = result_df["context_precision"].mean()
    avg_context_recall = result_df["context_recall"].mean()
    
    print(f"Faithfulness 平均值: {avg_faithfulness:.4f}")
    print(f"Answer Relevancy 平均值: {avg_answer_relevancy:.4f}")
    print(f"Context Precision 平均值: {avg_context_precision:.4f}")
    print(f"Context Recall 平均值: {avg_context_recall:.4f}")
    
    result_df.to_json("./eval/result/evaluation_results.json", orient="records", force_ascii=False, indent=4)
    print("评估结果已保存至 ./eval/result/evaluation_results.json")

if __name__ == "__main__":
    main()
