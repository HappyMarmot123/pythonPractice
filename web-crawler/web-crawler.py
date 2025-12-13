import requests
from bs4 import BeautifulSoup

# 크롤링할 대상 URL (예: 네이버 뉴스 홈)
URL = "https://news.naver.com/"

try:
    # 1. requests.get()으로 웹페이지에 GET 요청을 보냅니다.
    response = requests.get(URL)
    # 요청이 성공했는지 확인합니다 (응답 코드 200이면 성공).
    response.raise_for_status() 

    # 2. 응답받은 HTML 텍스트를 가져옵니다.
    html_content = response.text
    
except requests.exceptions.RequestException as e:
    print(f"웹 요청 중 오류가 발생했습니다: {e}")
    # 프로그램 종료
    exit()

print("✅ 웹페이지 HTML 가져오기 성공!")

soup = BeautifulSoup(html_content, 'html.parser')
news_container = soup.find('div', class_='main_brick')

if news_container:
    headline_links = news_container.find_all('strong', class_='cnf_news_title')
    print("\n📰 실시간 뉴스 헤드라인 📰")
    print("-" * 30)

    count = 0
    for link in headline_links:
        title = link.get_text(strip=True)
        if title:
            print(f"{count+1}. {title}")
            count += 1
            if count >= 10:
                break
    
    if count == 0:
        print("헤드라인 없음")
else:
    print("컨테이너 없음")

print("-" * 30)