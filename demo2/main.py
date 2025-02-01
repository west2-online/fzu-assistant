import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database.chroma_db import chroma_db
from query.query import query

from config.config import Config
Conf = Config()

if __name__ == "__main__":
    db = chroma_db
    s = input("输入问题：")
    print(query(db, s))
    