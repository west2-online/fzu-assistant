from FlagEmbedding import FlagReranker
from langchain_core.documents import Document
import typing as t

# 使用 BAAI/bge-reranker-v2-m3，可以尝试换成 https://huggingface.co/BAAI/bge-reranker-v2-minicpm-layerwise#for-llm-based-layerwise-reranker
rrk_model = FlagReranker('BAAI/bge-reranker-v2-m3', devices=["cuda:0"], use_fp16=True) 

class Rerank:

    def __init__(self, model):
        self.model = model

    def __call__(self, query, documents:t.List[Document]) -> t.List[Document]:

        input_pairs = [(query, doc.page_content) for doc in documents]
        
        scores = self.model.compute_score(input_pairs)
        
        ranked_documents = [doc for _, doc in sorted(zip(scores, documents), key = lambda x: x[0])]
        
        return ranked_documents

if __name__ == '__main__':

    query = "福州大学的校训和精神是什么？"
    documents = [
        Document(page_content = "福州大学的校训为“明德至诚，博学远志”。学校秉承并践行“三种精神”：以张孤梅同志为代表的艰苦奋斗的创业精神、以卢嘉锡先生为代表的严谨求实的治学精神、以魏可镁院士为代表的勇于拼搏的奉献精神。同时，学校营造“守正创新、彰显特色、开放包容、追求卓越”的新时代校园文化，积累了丰富的办学经验，形成了鲜明的办学特色。"),
        Document(page_content = "福州大学是国家“双一流”建设高校、国家“211工程”重点建设大学，由福建省人民政府与国家教育部共建。学校创建于1958年，现已发展成为一所以工为主、理工结合，涵盖理、工、经、管、文、法、艺、医等多学科协调发展的重点大学。"),
        Document(page_content = "福州大学自建校以来，已为国家培养了全日制毕业生33万余人，涵盖多个学科领域，为社会输送了大量高素质人才。"),
        Document(page_content = "福州大学自建校以来，已为国家培养了全日制毕业生33万余人，涵盖多个学科领域，为社会输送了大量高素质人才。"),
        Document(page_content = "福州大学设有27个学院（其中包括1个独立学院——至诚学院，1个中外合作办学学院）以及1家附属省立医院。")
    ]
    rrk = Rerank(rrk_model)
    ranked_docs = rrk(query, documents)
    print("Ranked Documents:")
    for i, doc in enumerate(ranked_docs, 1):
        print(f"{i}. {doc}")