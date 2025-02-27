import torch
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# 初始化嵌入模型
embedding_model = HuggingFaceEmbeddings(model_name="TencentBAC/Conan-embedding-v1")

# 初始化大模型
def load_llm(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device="cuda" if torch.cuda.is_available() else "cpu")
    return HuggingFacePipeline(pipeline=pipe)

# 初始化 RAG 和 GraphRAG
def init_rag(llm, faiss_index):
    return RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=faiss_index.as_retriever())

def init_graph_rag(llm, neo4j_graph):
    # 这里可以根据需要实现 GraphRAG 的逻辑
    pass

# 攻击技术实现
def adversarial_semantic_crafting(target_query, llm, num_iterations=100, learning_rate=0.01):
    input_ids = llm.tokenizer.encode(target_query, return_tensors="pt")
    input_ids.requires_grad = True

    for _ in range(num_iterations):
        outputs = llm.model(input_ids)
        loss = -outputs.logits.mean()  # 最大化相似性
        loss.backward()
        input_ids = input_ids + learning_rate * input_ids.grad
        input_ids = torch.clamp(input_ids, 0, llm.tokenizer.vocab_size - 1)

    return llm.tokenizer.decode(input_ids[0], skip_special_tokens=True)

def pairwise_loss_optimization_trigger(trigger, target_document, llm, num_iterations=100, learning_rate=0.01):
    trigger_ids = llm.tokenizer.encode(trigger, return_tensors="pt")
    target_ids = llm.tokenizer.encode(target_document, return_tensors="pt")
    trigger_ids.requires_grad = True

    for _ in range(num_iterations):
        combined_ids = torch.cat([trigger_ids, target_ids], dim=1)
        outputs = llm.model(combined_ids)
        loss = -outputs.logits.mean()  # 最大化相似性
        loss.backward()
        trigger_ids = trigger_ids + learning_rate * trigger_ids.grad
        trigger_ids = torch.clamp(trigger_ids, 0, llm.tokenizer.vocab_size - 1)

    return llm.tokenizer.decode(trigger_ids[0], skip_special_tokens=True)

def generate_connecting_sentence(prompt, llm, max_length=50):
    input_ids = llm.tokenizer.encode(prompt, return_tensors="pt")
    output = llm.model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    return llm.tokenizer.decode(output[0], skip_special_tokens=True)

def embed_query_in_document(query, document):
    return f"{document} {query}"

def generate_malicious_document(prompt, llm, max_length=200):
    input_ids = llm.tokenizer.encode(prompt, return_tensors="pt")
    output = llm.model.generate(input_ids, max_length=max_length, num_return_sequences=1)
    return llm.tokenizer.decode(output[0], skip_special_tokens=True)

# 攻击测试
def attack_test(llm, target_query, malicious_document):
    # ASC
    asc_result = adversarial_semantic_crafting(target_query, llm)
    print("ASC Result:", asc_result)

    # PAT
    pat_result = pairwise_loss_optimization_trigger("触发器", malicious_document, llm)
    print("PAT Result:", pat_result)

    # SEO
    seo_result = generate_malicious_document(target_query, llm)
    print("SEO Result:", seo_result)

# 主函数
if __name__ == "__main__":
    # 初始化大模型
    llm = load_llm("deepseek-ai/DeepSeek-R1-Distill-Qwen-7B")  # 或 Qwen/Qwen2.5-7B-Instruct

    # 目标查询和恶意文档
    target_query = "福州大学校训是什么？"
    malicious_document = "这是一个恶意文档，包含误导信息。"

    # 进行攻击测试
    attack_test(llm, target_query, malicious_document)