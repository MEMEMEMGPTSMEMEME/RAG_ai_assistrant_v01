# core/html_downloader.py

import os
import requests
from urllib.parse import urlparse
from tqdm import tqdm

SAVE_DIR = "storage/html"
FAIL_LOG = "storage/download_failed.txt"

def sanitize_filename(url_path):
    name = url_path.strip("/").replace("/", "_")
    return name if name else "index"

def download_html(url, save_dir):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            parsed = urlparse(url)
            filename = sanitize_filename(parsed.path)
            full_path = os.path.join(save_dir, f"{filename}.html")
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(r.text)
            return True
        else:
            raise Exception(f"Status {r.status_code}")
    except Exception as e:
        with open(FAIL_LOG, "a", encoding="utf-8") as f:
            f.write(f"{url} - {e}\n")
        return False

def download_all_html_from_file(link_file="all_links.txt"):
    if not os.path.exists(link_file):
        print(f"[ERROR] 링크 파일 없음: {link_file}")
        return

    os.makedirs(SAVE_DIR, exist_ok=True)
    success_count = 0

    with open(link_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in tqdm(urls, desc="📥 HTML 다운로드 중"):
        if download_html(url, SAVE_DIR):
            success_count += 1

    print(f"\n✅ 총 {success_count}/{len(urls)}개 HTML 저장 완료 → {SAVE_DIR}")
