from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import os
from groq import Groq
from datetime import datetime, timezone, timedelta

from git_push import commit_to_another_repo
from post_blogger import post_to_blogger

def get_naver_land_news_text():
    # Headless 브라우저 옵션
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("user-agent=Mozilla/5.0")

    # 웹드라이버 실행
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://land.naver.com/news/headline.naver")

    # JavaScript 로딩 대기
    time.sleep(3)

    # 뉴스 제목 추출
    news_items = driver.find_elements(By.CSS_SELECTOR, "#land_news_list li")

    results = []
    for item in news_items:
        try:
            title = item.find_element(By.CSS_SELECTOR, "a").text.strip()
            link = item.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            img = item.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
            results.append(f"{title}\n{link}\n{img}")
        except:
            continue

    driver.quit()
    return results

def ask(role, content):
    client = Groq()
    completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": content},
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )
    result = ""
    for chunk in completion:
        delta = chunk.choices[0].delta
        content_piece = delta.content if delta and delta.content else ""
        print(content_piece, end="", flush=True)
        result += content_piece
    return result

def write_blog(title, img, content):
    tz = timezone(timedelta(hours=9))
    now = datetime.now(tz)
    formatted = now.isoformat()

    result = """---
title: %s
date: %s
description: %s
draft: false
author: 벤틀리 집사
cover: %s
theme: light
---

%s""" % (title, formatted, title, img, content)
    return result

def main():
    news_list = get_naver_land_news_text()
    content = "\n\n".join(news_list)
    summary = ask("only 서울 지역 아파트 정보, markdown 형식으로 작성, No bold", content + "\n\n서울 아파트 관련 뉴스 10개 내외로 선정, 부동산 전문가로서의 의견도 추가해줘")
    img = ask("url 주소에서 type=nf142_103는 제외하고 추출", content + "random으로 글의 image url 하나만 추출")
    title = ask("title 은 plain text", summary + "위 내용을 기반으로 MrBeast 스타일의 뉴스 제목을 자극적이고 검색이 잘 될거 같은 제목 1개만 작성")
    title = title.replace("**", "")  # Remove any ** characters from title
    result = write_blog(title, img, summary)

    from datetime import datetime
    from zoneinfo import ZoneInfo
    kst = ZoneInfo("Asia/Seoul")
    today = datetime.now(tz=kst).strftime("%Y-%m-%d-%H")

    commit_to_another_repo(result, username="zipsa-ai", repo_name="zipsa-ai.github.io", posts_path="content/posts")
    commit_to_another_repo(result, username="zipsa-ai", repo_name="youtube-data", posts_path=f"{today}")
 
    try:
        # Write to blogger
        summary += """
## Reference

[더 많은 뉴스로 이동](https://sunshout.tistory.com)"""
        blog_id = 30091571
        post_to_blogger(title, summary, blog_id)
        blog_id = 1381865439607080595
        post_to_blogger(title, summary, blog_id)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    
    main()
