from langchain_core.documents import Document
import json
import os


class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load(self):
        docs = []
        print(os.listdir(self.data_dir))
        for file_path in os.listdir(self.data_dir):
            full_path = os.path.join(self.data_dir, file_path)
            with open(full_path, "r", encoding="UTF-8") as f:
                qa_lst = json.load(f)
            qa = json.dumps(qa_lst, ensure_ascii=False)
            doc = Document(
                page_content=qa,
                metadata={"source": full_path}
            )
            docs.append(doc)
        return docs

    def load_and_split(self):
        docs = []
        print("files:", os.listdir(self.data_dir))
        for file_path in os.listdir(self.data_dir):
            full_path = os.path.join(self.data_dir, file_path)
            with open(full_path, "r", encoding="UTF-8") as f:
                qa_lst = json.load(f)
            for qa in qa_lst:
                doc = Document(page_content=str(qa), metadata={"source": full_path})
                docs.append(doc)
        return docs


if __name__ == "__main__":
    loader = DataLoader("../../data")
    documents = loader.load_and_split()
    print(len(documents), documents[0])
