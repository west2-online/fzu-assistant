from typing import Any
from langchain_community.vectorstores import Chroma
# from langchain.text_splitter import RecursiveJsonSplitter
from langchain_cohere import CohereEmbeddings
import os
import json
import hashlib
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from config.config import Config
Conf = Config()

class chroma_db:
    def __init__(self, data_f:str = Conf.chroma_savefile, model:str = Conf.embedding_model):
        if(data_f is None or not os.path.exists(data_f)):
            self_dir = os.path.dirname(os.path.abspath(__file__))
            if(not os.path.exists(os.path.join(self_dir, '..', 'data'))):
                os.makedirs(os.path.join(self_dir, '..', 'data'))
                if(not os.path.exists(os.path.join(self_dir, '..', 'data', 'chroma'))):
                    os.makedirs(os.path.join(self_dir, '..', 'data', 'chroma'))
            data_file = os.path.join(self_dir, '..', 'data', 'chroma')
        self.db = Chroma(persist_directory = data_file, embedding_function = CohereEmbeddings(model = model))
        # self.splitter = RecursiveJsonSplitter(200, 50)

    def generate_id(self, text:str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def add_from_json(self, json_datas:list[dict], with_print:bool = True):
        try:
            ids = [self.generate_id(json_data['question']) for json_data in json_datas]
            splitted_datas = [json.dumps(json_data, ensure_ascii = False) for json_data in json_datas]
            # print(ids)
            self.db.add_texts(texts = splitted_datas, ids = ids, metadatas=[{"id": idd} for idd in ids])
            if(with_print):
                print(f"\033[32m添加成功\033[0m，共上传 {len(ids)} 对问答。")
            else:
                return len(ids)
        except Exception as e:
            if(with_print):    
                print(f"\033[31m添加失败\033[0m，错误：{e}")
            else:
                return e
        

    def add_from_json_file(self, file:str):
        json_datas = json.load(open(file, "r", encoding="UTF-8"))
        # print(json_datas)
        self.add_from_json(json_datas)

    def query_by_question(self, question:str, top_k:int = Conf.topk) -> Any:
        return self.db.similarity_search(question, top_k)

    def delete_by_id(self, id:str):
        try:
            self.db.delete([id])
            print("\033[32m删除成功\033[0m")
            return True
        except Exception as e:
            print(f"\033[31m删除失败\033[0m，错误：{e}")
            return False

    def delete_by_question(self, question:str) -> bool:
        res = self.query_by_question(question, 1)[0]
        # print(res.page_content)
        ques = json.loads(res.page_content)['question']
        if(question != ques):
            print("\033[31m删除失败\033[0m，错误：未找到指定问题。是否在寻找：" + ques)
            return False
        return self.delete_by_id(res.metadata['id'])

    def update_from_json(self, json_datas:list[dict]):
        succ_count = len(self.db)
        ids = [self.generate_id(json_data['question']) for json_data in json_datas]
        # print(f'删除数量{len(ids)}')
        self.db.delete(ids=ids)
        succ_count -= len(self.db)
        # print(f"共成功删除 {succ_count} 对问答")
        res = self.add_from_json(json_datas, with_print = False)
        if(isinstance(res, int)):
            print(f"\033[32m更新成功\033[0m，其中更新 {succ_count} 对问答，新建 {res - succ_count} 对问答")
        else:
            print(f"\033[31m更新失败\033[0m，错误： {res}")
            print(type(res))

    def update_from_file(self, file:str):
        json_datas = json.load(open(file, "r", encoding="UTF-8"))
        self.update_from_json(json_datas)

if __name__ == "__main__": #TEST
    # os.environ["COHERE_API_KEY"] = ""
    cdb = chroma_db()
    # print(cdb.query_by_question("1"))
    cdb.delete_by_question("2")
    # cdb.update_from_file("D:/Games/EA/Code/LLM/git/demo2/test/test.json")
