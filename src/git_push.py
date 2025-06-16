import os
import subprocess
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo

GITHUB_TOKEN = os.environ["GIT_TOKEN"]
TARGET_BRANCH = os.environ.get("TARGET_BRANCH", "main")

COMMIT_AUTHOR_NAME = os.environ.get("COMMIT_AUTHOR_NAME", "017.Bentley")
COMMIT_AUTHOR_EMAIL = os.environ.get("COMMIT_AUTHOR_EMAIL", "017.bentley@spaceone.ai")

def run(cmd, cwd=None):
    print(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def commit_to_another_repo(markdown_content, username="zipsa-ai", repo_name="zipsa-ai.github.io", posts_path="content/posts"):
    kst = ZoneInfo("Asia/Seoul")
    today = datetime.now(tz=kst).strftime("%Y-%m-%d-%H")
    filename = f"{today}.md"

    # 설정
    target_repo_url = f"https://{GITHUB_TOKEN}@github.com/{username}/{repo_name}.git"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Clone
        run(f"git clone --branch {TARGET_BRANCH} {target_repo_url} .", cwd=tmpdir)

        # 2. Write file
        full_posts_path = os.path.join(tmpdir, posts_path)
        os.makedirs(full_posts_path, exist_ok=True)
        file_path = os.path.join(full_posts_path, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # 3. Git config
        run(f"git config user.name \"{COMMIT_AUTHOR_NAME}\"", cwd=tmpdir)
        run(f"git config user.email \"{COMMIT_AUTHOR_EMAIL}\"", cwd=tmpdir)

        # 4. Commit & Push
        run("git add .", cwd=tmpdir)
        run(f"git commit -m \"[Post] {filename}\"", cwd=tmpdir)
        run(f"git push origin {TARGET_BRANCH}", cwd=tmpdir)

# 예시 실행
if __name__ == "__main__":
    title = "서울 아파트 분양 핵심 요약"
    summary = "# 서울 아파트 분양 요약\n\n강남, 용산 일대에서 3일 만에 완판된 단지들이 늘고 있습니다..."
    commit_to_another_repo(summary)
