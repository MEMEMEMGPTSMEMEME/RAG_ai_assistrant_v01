# pipeline/data_ingestion.py

import os
from dotenv import load_dotenv

from core.crawler import crawl_multiple_domains
from core.html_downloader import download_all_html_from_file
from core.parser import parse_all_html
from core.embedder import embed_documents

load_dotenv()

SEED_URLS = [
    "https://docs.blender.org/manual/en/4.0/index.html",
    "https://helpx.adobe.com/photoshop/user-guide.html"
]

LINK_FILE = os.getenv("LINK_FILE", "all_links.txt")

def run_data_ingestion(seed_urls=SEED_URLS):
    print("🔗 [1/4] 링크 수집 중...")
    crawl_multiple_domains(seed_urls, output_file=LINK_FILE)

    print("🌐 [2/4] HTML 다운로드 중...")
    download_all_html_from_file(LINK_FILE)

    print("📝 [3/4] 텍스트 추출 중...")
    parse_all_html()

    print("🧠 [4/4] 문서 임베딩 중...")
    embed_documents()

    print("✅ 전체 데이터 인제스트 완료!")

if __name__ == "__main__":
    run_data_ingestion()
