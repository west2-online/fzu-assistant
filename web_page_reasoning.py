import torch
import streamlit
torch.classes.__path__ = [] 
import streamlit as st
from NaiveRAG import NaiveRAG
# from NaiveRAG_Guardrails_AI import GuardrailsRAG as NaiveRAG
from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from itertools import zip_longest
st.set_page_config(page_title="智能助手", page_icon="🧠")
# 修复异步事件循环冲突
# import asyncio
# asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

rag = NaiveRAG(chat_llm=chat_llm,
                tool_llm=tool_llm,
                embeddings=embeddings,
                vector_storage_dir=conf.storage_dir.vector,
                top_k=conf.top_k)


# 设置页面标题
# st.title("🤖 智能助手")

# 初始化对话历史
if "messages" not in st.session_state:
    st.session_state.messages = []
if "token_usage" not in st.session_state:
    st.session_state.token_usage = []
# 显示历史消息
for message, tk in zip_longest(st.session_state.messages, st.session_state.token_usage):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            st.caption(f"消耗 Token：{tk}")
def format_response(response: str):
    response = response.split("</think>")
    if len(response) == 1:
        return f"""
        > {response[0].replace("<think>", "").replace("</think>", "").replace("\n", "")}
        """
    else:
        return f"""
        > {response[0].replace("<think>", "").replace("</think>", "").replace("\n", "")}
        {response[1]}
        """
# 处理用户输入
if prompt := st.chat_input("请输入您的问题"):
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("思考中"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in rag.stream(query=prompt, history=st.session_state.messages):
                if hasattr(chunk, "content"):
                    full_response += chunk.content
                elif isinstance(chunk, str):
                    full_response += chunk
                response_placeholder.markdown(format_response(full_response) + "▌")  
            response_placeholder.markdown(format_response(full_response))
            st.session_state.token_usage.append(None)
            st.session_state.token_usage.append(chunk["response"].usage_metadata.get("total_tokens", 0))
            st.caption(f"消耗 Token：{chunk["response"].usage_metadata.get("total_tokens", 0)}")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": format_response(full_response)
    })