import json
import os

class Config:
    def __init__(self):
        self_dir = os.path.dirname(os.path.abspath(__file__))
        conf_dir = os.path.join(self_dir, '.', 'config.json')
        with open(conf_dir, "r", encoding = "UTF-8") as f:
            d = f.read()
        conf = json.loads(d)
        self.chat_model = conf['chat model']
        self.chroma_savefile = conf['chroma_db']['save file']
        self.embedding_model = conf['chroma_db']['embedding model']
        self.topk = conf['top_k']
        os.environ["COHERE_API_KEY"] = conf['COHERE API KEY']