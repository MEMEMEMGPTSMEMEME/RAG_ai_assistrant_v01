# core/crawler.py

import os
import time
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

SKIP_EXTENSIONS = [".pdf", ".zip", ".js", ".css", ".ico", ".png", ".jpg", ".jpeg", ".svg"]
MAX_LINKS_PER_DOMAIN = 1000
WAIT_SEC = 1.2

def init_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(options=options)

def should_skip_url(url):
    return any(url.lower().endswith(ext) for ext in SKIP_EXTENSIONS)

def crawl_domain(seed_url, output_file="all_links.txt", max_links=MAX_LINKS_PER_DOMAIN):
    visited = set()
    to_visit = [seed_url]
    parsed_seed = urlparse(seed_url)
    allowed_domain = parsed_seed.netloc

    os.makedirs("storage/html", exist_ok=True)

    driver = init_driver()

    with open(output_file, "a", encoding="utf-8") as f:
        while to_visit and len(visited) < max_links:
            url = to_visit.pop(0)
            if url in visited:
                continue
            try:
                driver.get(url)
                time.sleep(WAIT_SEC)
                print(f"🔗 수집 중: {url}")
                visited.add(url)

                anchors = driver.find_elements("tag name", "a")
                for a in anchors:
                    href = a.get_attribute("href")
                    if not href:
                        continue
                    joined = urljoin(url, href)
                    parsed = urlparse(joined)
                    if parsed.netloc != allowed_domain or should_skip_url(parsed.path):
                        continue
                    if joined not in visited and joined not in to_visit:
                        to_visit.append(joined)
                        f.write(joined + "\n")

            except WebDriverException as e:
                print(f"[ERROR] {url} 접근 실패: {e}")
                continue

    driver.quit()
    print(f"✅ {allowed_domain} 수집 완료 ({len(visited)}개 링크) → {output_file}")

def crawl_multiple_domains(seed_urls, output_file="all_links.txt"):
    # 초기화
    if os.path.exists(output_file):
        os.remove(output_file)

    for url in seed_urls:
        crawl_domain(url, output_file=output_file)
