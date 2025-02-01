import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database.chroma_db import chroma_db
from langchain_cohere import ChatCohere
import json

from config.config import Config
Conf = Config()

def query(db:chroma_db, question:str) -> str:
    chat_model = ChatCohere(
        model = Conf.chat_model
    )
    knowledges = db.query_by_question(question)
    # print(knowledges)
    knowledge = "\n".join([json.loads(k.page_content)['answer']
                            for k in knowledges])

    prompt = f"""
    基于以下知识回答问题：
    知识：
    {knowledge}
    问题：
    {query}
    """
    try:
        res = chat_model.invoke(prompt)
        return res.content
    except Exception as e:
        return e


if __name__ == "__main__": #TEST
    db = chroma_db()
    print(query(db, ""))