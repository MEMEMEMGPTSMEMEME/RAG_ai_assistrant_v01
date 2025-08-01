# api/server.py

from flask import Flask, request, jsonify
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import traceback
import threading
import subprocess
import pickle
import faiss

from sentence_transformers import SentenceTransformer

from pipeline.data_ingestion import run_data_ingestion
from core.embedder import INDEX_PATH, METADATA_PATH

load_dotenv()

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "message": "✅ RAG Assistant 서버 실행 중입니다.",
        "endpoints": ["/health", "/start_data_ingestion", "/ask"]
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/start_data_ingestion", methods=["POST"])
def start_data_ingestion():
    try:
        data = request.get_json()
        seed_urls = data.get("seed_urls")

        if not seed_urls or not isinstance(seed_urls, list):
            return jsonify({"error": "seed_urls (list) is required"}), 400

        print(f"[INFO] 수집 시작: {seed_urls}")
        run_data_ingestion(seed_urls)

        def git_push():
            try:
                print("[GIT] 자동 푸시 시작")
                subprocess.run(["python", "scripts/auto_git_push.py"], check=True)
                print("[GIT] 자동 푸시 완료")
            except Exception as e:
                print(f"[GIT ERROR] 자동 푸시 실패: {e}")

        threading.Thread(target=git_push).start()

        return jsonify({
            "status": "success",
            "message": "데이터 인제스트 완료. GitHub에 자동 푸시 완료 예정."
        }), 200

    except Exception as e:
        print("[ERROR] 인제스트 실패:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        query = data.get("query")
        if not query:
            return jsonify({"error": "query is required"}), 400

        if not os.path.exists(INDEX_PATH) or not os.path.exists(METADATA_PATH):
            return jsonify({"error": "벡터 인덱스/메타데이터 없음"}), 500

        print("🔍 질문 처리 중:", query)

        model = SentenceTransformer(os.getenv("MODEL_NAME", "all-MiniLM-L6-v2"))
        index = faiss.read_index(INDEX_PATH)

        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)

        query_embedding = model.encode([query])
        top_k = min(3, index.ntotal)
        _, indices = index.search(query_embedding, top_k)

        results = []
        for i in indices[0]:
            if 0 <= i < len(metadata):
                fname = metadata[i]["filename"]
                fpath = os.path.join(os.getenv("TEXT_DIR", "storage/parsed_docs"), fname)
                if os.path.exists(fpath):
                    with open(fpath, "r", encoding="utf-8") as f:
                        snippet = f.read(1000)
                        results.append({
                            "filename": fname,
                            "snippet": snippet
                        })

        return jsonify({"results": results}), 200

    except Exception as e:
        print("[ERROR] 질문 처리 실패:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("SERVER_PORT", 5000))
    app.run(host="0.0.0.0", port=port)
