import os
from langchain_cohere import ChatCohere
from langchain_community.vectorstores import Chroma
from split import split_and_save
# from langchain.schema import SystemMessage,HumanMessage,AIMessage

os.environ["COHERE_API_KEY"] = "COHERE_API_KEY" # 填入cohere api key

chat = ChatCohere(
    model = "command-r-plus"
)

db = split_and_save("file") #填入要保存的文件地址

query = "询问"#填入询问内容

sknowledge = db.similarity_search(query, k = 2)

knowledge = "\n".join([kno.page_content for kno in sknowledge])

prompt = f"""
基于以下内容回答问题：
内容：
{knowledge}
问题：
{query}
"""
res = chat.invoke(prompt)
print(res)