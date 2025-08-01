# core/parser.py

import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

HTML_DIR = os.getenv("HTML_DIR", "storage/html")
TEXT_DIR = os.getenv("TEXT_DIR", "storage/parsed_docs")

os.makedirs(TEXT_DIR, exist_ok=True)

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "header", "footer", "nav", "noscript"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

def parse_html_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
        return clean_html(html)
    except Exception as e:
        print(f"[ERROR] 파일 처리 실패: {filepath} ({e})")
        return None

def parse_all_html():
    if not os.path.exists(HTML_DIR):
        print(f"[ERROR] 입력 폴더가 존재하지 않습니다: {HTML_DIR}")
        return

    html_files = [f for f in os.listdir(HTML_DIR) if f.endswith(".html")]
    count = 0

    for filename in html_files:
        in_path = os.path.join(HTML_DIR, filename)
        out_path = os.path.join(TEXT_DIR, filename.replace(".html", ".txt"))

        cleaned = parse_html_file(in_path)
        if cleaned:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(cleaned)
            count += 1
            print(f"✅ 텍스트 추출 완료: {filename}")

    print(f"\n📄 총 {count}/{len(html_files)}개 HTML → 텍스트 변환 완료")
