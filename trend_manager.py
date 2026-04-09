import json
import random
import requests
import config
from google import genai
from datetime import datetime  # 날짜 처리를 위해 추가

# Gemini 클라이언트 초기화
client = genai.Client(api_key=config.GEMINI_API_KEY)

def generate_dynamic_keyword():
    """
    오늘 날짜를 기준으로 전 세계 사람들이 가장 관심을 가질 만한 핫한 주제를 생성합니다.
    """
    # [수정] 오늘 날짜 가져오기 (예: 2026-02-03)
    today_date = datetime.now().strftime('%Y-%m-%d')

    # 프롬프트에 오늘 날짜를 명시하여 최신성 강조
    prompt = f"""
    Today is {today_date}. 
    Generate 3 highly viral and trending search keywords for a global English blog.
    The topics should be what people are most curious about right now, such as:
    - Viral social media trends or internet culture
    - Breaking entertainment, celebrity news, or movie/show releases
    - Shocking global events, lifestyle hacks, or travel trends
    - Revolutionary tech or health discoveries that interest everyone
    Return ONLY the 3 keywords separated by commas.
    Example: Oscar 2026 predictions, viral TikTok lifestyle hack, global travel hidden gems
    """

    try:
        print(f"🗓️ Today's Date: {today_date}")
        response = client.models.generate_content(model=config.MODEL_NAME, contents=prompt)
        # 생성된 텍스트에서 키워드 추출 및 정리
        keywords = [k.strip() for k in response.text.strip().split(',')]
        selected = random.choice(keywords)
        print(f"🪄 AI Generated Keyword: '{selected}'")
        return selected
    except Exception as e:
        print(f"❌ AI Keyword Generation Failed: {e}")
        return None

def get_google_trend():
    """
    생성된 주제로 Serper.dev 뉴스를 가져와 블로그 글감을 확정합니다.
    """
    print("📡 Connecting to Serper.dev (Google News)...")

    # 1. 먼저 AI에게 실시간 키워드 요청
    query = generate_dynamic_keyword()

    # 2. AI 실패 시 또는 결과가 없을 때 사용할 고정 폴백(Fallback) 키워드 리스트
    fallback_keywords = [
        "latest AI technology news",               # 최신 AI 기술 뉴스  
        "remote work productivity tips",         # 원격 근무 생산성 팁
        "global economic trends 2026",          # 2026년 글로벌 경제 동향
        "new startup business ideas",         # 새로운 스타트업 비즈니스 아이디어
        "health and wellness trends",        # 건강 및 웰니스 트렌드
        "sustainable energy news",           # 지속 가능한 에너지 뉴스
        "future technology 2026",            # 미래 기술 2026
        # --- 테크 & AI (가장 클릭률 높음) ---
        "latest Gemini AI updates and features",   # 제미나이 최신 소식
        "Apple and Google AI partnership news",    # 애플-구글 AI 동맹 관련
        "NVIDIA and semiconductor market trends",  # 엔비디아 및 반도체 동향
        
        # --- 경제 & 재테크 (사용자 전문 분야) ---
        "US Stock market forecast 2026",           # 미국 주식 시장 전망
        "best high-dividend stocks for 2026",      # 2026년 최고 배당주
        "Federal Reserve interest rate news",      # 연준 금리 뉴스
        
        # --- 미래 기술 & 스타트업 ---
        "breakthrough in sustainable energy tech", # 에너지 기술 혁신
        "top 10 emerging tech startups 2026",      # 10대 유망 스타트업
        "future of space exploration news",       # 우주 탐사 뉴스
        
        # --- 글로벌 라이프스타일 ---
        "digital nomad visa updates 2026",         # 디지털 노마드 비자 뉴스
        "next-gen wellness and longevity tech"     # 차세대 웰빙 및 장수 기술
    ]

    # AI가 키워드를 가져오지 못했다면 기존 방식대로 랜덤 선택
    if not query:
        query = random.choice(fallback_keywords)
        print(f"⚠️ Using Fallback Viral Keyword: '{query}'")

    # 3. Serper API 호출 설정
    url = "https://google.serper.dev/news"
    payload = json.dumps({
        "q": query,
        "gl": "us",  # 국가: 미국
        "hl": "en",  # 언어: 영어
        "num": 3 
    })
    headers = {
        'X-API-KEY': config.SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        
        if 'news' in data and len(data['news']) > 0:
            pick = data['news'][0]
            clean_title = pick['title'].split(" - ")[0].strip()
            print(f"🔥 Trending Topic Found: {clean_title}")
            print(f"🔗 Source Link: {pick['link']}")
            return clean_title
            
        else:
            print(f"⚠️ 검색 결과가 없습니다.: {query}")
            return "Top Global Tech Innovations to Watch in 2026"

    except Exception as e:
        print(f"❌ 서버 API 오류: {e}")
        return "Future Technology Trends: What to Expect in 2026"

if __name__ == "__main__":
    print("🧪 [테스트] 고도화된 트렌드 매니저 테스트를 시작합니다...")
    result = get_google_trend()
    print("-" * 30)
    print(f"✅ 최종 선정 대중적 주제: {result}")