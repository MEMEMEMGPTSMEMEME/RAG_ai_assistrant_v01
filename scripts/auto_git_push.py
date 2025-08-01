# scripts/auto_git_push.py

import subprocess
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GIT_USERNAME = os.getenv("GIT_USERNAME", "auto-bot")
GIT_EMAIL = os.getenv("GIT_EMAIL", "auto@bot.com")
REPO_URL = os.getenv("REPO_URL")
BRANCH = os.getenv("GIT_BRANCH", "main")  # ⬅️ 수정됨: 기본 브랜치를 'main'으로 설정

if not REPO_URL:
    print("❌ REPO_URL 환경변수가 설정되지 않았습니다.")
    exit(1)

# Git 설정
subprocess.run(["git", "config", "--global", "user.name", GIT_USERNAME])
subprocess.run(["git", "config", "--global", "user.email", GIT_EMAIL])

# 파일 추가 및 커밋
subprocess.run(["git", "add", "."])
commit_msg = f"📦 auto: 문서 자동 수집 및 벡터화 - {datetime.now().isoformat()}"
subprocess.run(["git", "commit", "-m", commit_msg])

# 푸시
push_result = subprocess.run(["git", "push", "origin", BRANCH], capture_output=True, text=True)

if push_result.returncode == 0:
    print("✅ GitHub 자동 푸시 성공")
else:
    print("❌ GitHub 푸시 실패")
    print(push_result.stderr)
