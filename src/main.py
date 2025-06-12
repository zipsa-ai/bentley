from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
from groq import Groq
from datetime import datetime, timezone, timedelta

from git_push import commit_to_another_repo

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


if __name__ == "__main__":
    news_list = get_naver_land_news_text()
    content = "\n\n".join(news_list)
    summary = ask("markdown 문서형식", content + "\n\n위 내용중 서울 지역 아파트 가격과 분양 뉴스만 선별해서 요약하고 전문가로서 의견도 추가해줘")
    img = ask("url 주소에서 type=nf142_103는 제외하고 추출", content + "가장 인기 있는 글의 image url 하나만 추출")
    title = ask("title 은 plain text", summary + "위 내용을 기반으로 MrBeast 스타일의 뉴스 제목을 자극적이고 검색이 잘 될거 같은 제목 1개만 작성")
    result = write_blog(title, img, summary)
    print("#" * 50)
    print("title: ", title)
    print(summary)
    print("-" * 200)
    print(result)

    commit_to_another_repo(result)
