from flask import Flask, Response, request, json
import json

from llms import chat_llm, tool_llm
from embeddings import embeddings
from config import conf
from RAGFusion import RAGFusion

app = Flask(__name__)

rag_fusion = RAGFusion(chat_llm=chat_llm,
                        tool_llm=tool_llm,
                        embeddings=embeddings,
                        vector_storage_dir=conf.storage_dir.vector,
                        top_k=conf.top_k)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completion():
    data = request.json
    messages = data.get('messages', [])

    def generate():
        try:
            # 尝试传原始JSON
            try:
                response_stream = rag_fusion.query(messages)
            except TypeError:
                # 如果失败，就转换成字符串
                input_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                response_stream = rag_fusion.query(input_text)

            for chunk in response_stream:
                yield json.dumps({
                    "answer": chunk,
                    "end_of_stream": False
                }) + '\n'

            yield json.dumps({"answer": "", "end_of_stream": True}) + '\n'

        except Exception as e:
            yield json.dumps({
                "answer": f"[ERROR] {str(e)}",
                "end_of_stream": True
            }) + '\n'

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(port=5000)
