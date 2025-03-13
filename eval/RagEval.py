import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)
import json
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
from _config import _conf
from config import conf
os.environ["ZHIPUAI_API_KEY"] = _conf.ZHIPU.ZHIPUAI_API_KEY
if _conf.Rag.Rerank :
    from utils import rrk_model
else:
    rrk_model = None

def initialize_zhipuai_models():
    zhipu_chat = ChatZhipuAI(model=_conf.ZHIPU.Model_name)
    zhipu_embedding = ZhipuAIEmbeddings(model=_conf.ZHIPU.embedding)
    return LangchainLLMWrapper(zhipu_chat), LangchainEmbeddingsWrapper(zhipu_embedding)


def generate_test_results():
    if not os.path.exists(_conf.Storage_dir.Testset_path + "/testset.json"):
        print("未找到测试数据，正在生成...")
        generate_testset()
    
    with open(_conf.Storage_dir.Testset_path + "/testset.json", "r", encoding="utf-8") as f:
        test_data = json.load(f)
    
    # 初始化 RAGFusion
    rag_class = globals()[_conf.Rag.RagName]  # 获取类对象
    rag = rag_class(chat_llm=chat_llm,
                           tool_llm=tool_llm,
                           embeddings=embeddings,
                           vector_storage_dir=conf.storage_dir.vector,
                           top_k=conf.top_k,
                           rerank_model=rrk_model)
    
    test_results = []
    for sample in tqdm(test_data, desc="Generating model answer"):
        question = sample.get("user_input", "")
        reference = sample.get("reference", "")
        retrieved_contexts = sample.get("reference_contexts", [])
        model_answer = rag.query(question)  # 由 RAGFusion 生成答案
        
        test_results.append({
            "user_input": question,  # 添加 user_input 列
            "query": question,
            "reference": reference,
            "retrieved_contexts": retrieved_contexts,
            "answer": model_answer
        })
    
    with open(_conf.Storage_dir.ModelAnswer_path + f"/{_conf.Rag.RagName}_{'rerank_' if _conf.Rag.Rerank else '_'}answer.json", "w", encoding="utf-8") as f:
        json.dump(test_results, f, ensure_ascii=False, indent=4)
    return test_results

def main():
    zhipu_llm, zhipu_embeddings = initialize_zhipuai_models()
    test_results = generate_test_results()
    df = pd.DataFrame(test_results)
    evalsets = Dataset.from_list(df.to_dict(orient="records"))
    
    # 设置模型
    faithfulness.llm = zhipu_llm
    answer_relevancy.llm = zhipu_llm
    answer_relevancy.embeddings = zhipu_embeddings
    context_recall.llm = zhipu_llm
    context_precision.llm = zhipu_llm
    
    print(f"正在评估{_conf.Rag.RagName}")
    
    # 评估
    result = evaluate(evalsets, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
    result_df = result.to_pandas()
    
    # 计算平均值
    avg_faithfulness = result_df["faithfulness"].mean()
    avg_answer_relevancy = result_df["answer_relevancy"].mean()
    avg_context_precision = result_df["context_precision"].mean()
    avg_context_recall = result_df["context_recall"].mean()
    
    print(f"{_conf.Rag.RagName}-Faithfulness 平均值: {avg_faithfulness:.4f}")
    print(f"{_conf.Rag.RagName}-Answer Relevancy 平均值: {avg_answer_relevancy:.4f}")
    print(f"{_conf.Rag.RagName}-Context Precision 平均值: {avg_context_precision:.4f}")
    print(f"{_conf.Rag.RagName}-Context Recall 平均值: {avg_context_recall:.4f}")
    
    # 创建只包含平均值的字典
    averages = {
        "avg_faithfulness": avg_faithfulness,
        "avg_answer_relevancy": avg_answer_relevancy,
        "avg_context_precision": avg_context_precision,
        "avg_context_recall": avg_context_recall
    }
    
    # 保存为JSON文件
    result_json_path = _conf.Storage_dir.Result_path + f"/{_conf.Rag.RagName}{'_rerank' if _conf.Rag.Rerank else ''}.json"
    with open(result_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(averages, json_file, ensure_ascii=False, indent=4)
    
    print(f"评估结果已保存至 {result_json_path}")





if __name__ == '__main__':
    main()
