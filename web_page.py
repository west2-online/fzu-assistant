import streamlit as st
from NaiveRAG import NaiveRAG
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
# from utils import rrk_model
rag = NaiveRAG(chat_llm=chat_llm,
                tool_llm=tool_llm,
                embeddings=embeddings,
                vector_storage_dir=conf.storage_dir.vector,
                top_k=conf.top_k)


# 设置页面标题
st.title("🤖 智能助手")

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题"):
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        for chunk in rag.stream(question=prompt, history=st.session_state.messages):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")  
        response_placeholder.markdown(full_response)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
