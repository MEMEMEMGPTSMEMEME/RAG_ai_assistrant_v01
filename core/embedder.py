# core/embedder.py

import os
import faiss
import pickle
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

load_dotenv()

TEXT_DIR = os.getenv("TEXT_DIR", "storage/parsed_docs")
VECTOR_DIR = os.getenv("VECTOR_DIR", "storage/vector_store")
MODEL_NAME = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")

INDEX_PATH = os.path.join(VECTOR_DIR, "faiss_index.index")
METADATA_PATH = os.path.join(VECTOR_DIR, "metadata.pkl")


def load_text_files(directory):
    texts, metadata = [], []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            path = os.path.join(directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        texts.append(content)
                        metadata.append({"filename": filename})
            except Exception as e:
                print(f"[ERROR] 파일 열기 실패: {filename} ({e})")
    return texts, metadata


def save_embeddings(index, metadata):
    os.makedirs(VECTOR_DIR, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)
    print(f"✅ FAISS 인덱스 저장 완료 → {INDEX_PATH}")


def embed_documents():
    print(f"🧠 임베딩 모델 로딩 중: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("📄 텍스트 불러오는 중...")
    texts, metadata = load_text_files(TEXT_DIR)

    if not texts:
        print("⚠️ 임베딩할 문서가 없습니다.")
        return

    print("📊 임베딩 생성 중...")
    embeddings = model.encode(texts, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    save_embeddings(index, metadata)
    print("✅ 문서 임베딩 완료.")
