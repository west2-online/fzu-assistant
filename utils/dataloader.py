from langchain_core.documents import Document
import json
import os
import typing as t

class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load(self):
        docs = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="UTF-8") as f:
                        qa_lst = json.load(f)
                    qa = json.dumps(qa_lst, ensure_ascii=False)
                    doc = Document(
                        page_content=qa,
                        metadata={"source": full_path}
                    )
                    docs.append(doc)
        return docs

    def load_and_split(self) -> t.List[Document]:
        docs = []
        for root, _, files in os.walk(self.data_dir):
            for file in files:
                if file.endswith('.json'):
                    full_path = os.path.join(root, file)
                    with open(full_path, "r", encoding="UTF-8") as f:
                        qa_lst = json.load(f)
                    for qa in qa_lst:
                        qa["source"] = file.removesuffix('.json')
                        doc = Document(
                            page_content=self.dict2str(qa),
                            metadata={"source": full_path}
                        )
                        docs.append(doc)
        return docs
    
    @staticmethod
    def dict2str(dct: t.Dict[str, str]):
        en_cn = {
            "date": "日期",
            "title": "标题",
            "link": "链接",
            "source": "来源",
            "introduction": "简介"
        }
        result = ""
        for key in dct.keys():
            value = dct.get(key, "")
            if en_cn.get(key, None) is not None:
                key = en_cn.get(key, None)
            result += f"{key}: {value}\n"
        return result


if __name__ == "__main__":
    loader = DataLoader("../data")
    documents = loader.load_and_split()
    print(len(documents), documents[0])
