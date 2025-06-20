from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

import requests
from bs4 import BeautifulSoup

def screenshot_url(url, output_path):
    """
    Takes a screenshot of the given URL using Selenium WebDriver and saves it as a PNG file.
    Args:
        url (str): The URL of the page to screenshot
        output_path (str): The file path to save the screenshot (should end with .png)
    """
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("user-agent=Mozilla/5.0")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        # Wait for the page to load
        time.sleep(3)
        driver.save_screenshot(output_path)
        print(f"Screenshot saved to {output_path}")
    finally:
        driver.quit()

def get_naver_news_content(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")
    # 네이버 뉴스 본문 영역은 id="dic_area" 또는 class="newsct_article" 등으로 구성됨
    # 최신 뉴스 기준
    content = soup.find("div", id="dic_area")
    if not content:
        # 구버전 뉴스 등 다른 구조 대응
        content = soup.find("div", class_="newsct_article")
    if content:
        return content.get_text(strip=True)
    else:
        return "본문을 찾을 수 없습니다."