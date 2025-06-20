from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

import time
import base64

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
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,3024")
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--disable-remote-fonts")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        driver.get(url)
        # Wait for the page to load
        time.sleep(2)
        #driver.get_full_page_screenshot_as_file(output_path)
            # DevTools 명령어로 전체 페이지 스크린샷
        result = driver.execute_cdp_cmd(
            "Page.captureScreenshot",
            {"captureBeyondViewport": True, "fromSurface": True}
        )
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(result['data']))
            
        print(f"Screenshot saved to {output_path}")
    finally:
        driver.quit()

def open_browser(url):
    """
    Takes a screenshot of the given URL using Selenium WebDriver and saves it as a PNG file.
    Args:
        url (str): The URL of the page to screenshot
        output_path (str): The file path to save the screenshot (should end with .png)
    """
    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("user-agent=Mozilla/5.1")
    options.add_argument("--disable-remote-fonts")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    # 마우스 위치에 빨간 원을 표시하는 JS 코드 삽입
    js_code = """
    (function() {
        var marker = document.createElement('div');
        marker.id = 'mouse-marker';
        marker.style.position = 'fixed';
        marker.style.width = '20px';
        marker.style.height = '20px';
        marker.style.border = '2px solid red';
        marker.style.borderRadius = '50%';
        marker.style.zIndex = 9999;
        marker.style.pointerEvents = 'none';
        marker.style.background = 'rgba(255,0,0,0.2)';
        document.body.appendChild(marker);

        document.addEventListener('mousemove', function(e) {
            marker.style.left = (e.clientX - 10) + 'px';
            marker.style.top = (e.clientY - 10) + 'px';
        });
    })();
    """
    driver.execute_script(js_code)
    actions = ActionChains(driver)

    actions.move_by_offset(150, 250).click().perform()
    for i in range(10):
        actions.move_by_offset(i, 0).click().perform()
        time.sleep(1)
    
    time.sleep(20)
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