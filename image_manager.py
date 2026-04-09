import time
import requests
import random
import urllib.parse
import config

def get_relevant_image_url(keyword, service=None, blog_id=None):
    """
    이미지 확보 전략:
    1. Pollinations AI (최대 3회 재시도)
    2. 실패 시 Unsplash (API 키 사용, 원본 URL 직접 반환)
    3. 최종 실패 시 Lorem Picsum (랜덤 이미지)
    """
    if not keyword:
        return "https://picsum.photos/1280/720"
    
    # 지수 백오프 대기 시간 (초)
    wait_times = [5, 15, 30] 
    
    # --- 1단계: Pollinations AI 시도 ---
    for attempt, wait_sec in enumerate(wait_times):
        try:
            seed = random.randint(1, 99999)
            encoded_keyword = urllib.parse.quote(keyword)
            pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_keyword}?width=1280&height=720&nologo=true&seed={seed}&model=flux"
            
            print(f"🤖 [시도 {attempt + 1}/3] Pollinations AI 이미지 생성 중...")
            response = requests.get(pollinations_url, timeout=40)
            
            if response.status_code == 200:
                print("✅ Pollinations AI 이미지 생성 성공!")
                return pollinations_url
            
            print(f"⚠️ 서버 응답 지연({response.status_code}). {wait_sec}초 후 다시 시도합니다.")
            time.sleep(wait_sec)

        except Exception as e:
            print(f"❌ AI 생성 중 오류 발생: {e}")
            time.sleep(wait_sec)

    # --- 2단계: Unsplash 백업 (구글 업로드 없이 URL 직접 사용) ---
    print("🚀 AI 생성이 원활하지 않아 Unsplash 이미지를 가져옵니다...")
    access_key = getattr(config, 'UNSPLASH_ACCESS_KEY', None)
    
    if access_key:
        try:
            search_url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape&client_id={access_key}"
            res = requests.get(search_url, timeout=10)
            if res.status_code == 200:
                img_data = res.json()
                unsplash_url = img_data['urls']['regular']
                print(f"✅ Unsplash 이미지 확보 성공: {unsplash_url}")
                return unsplash_url
            else:
                print(f"⚠️ Unsplash 응답 실패 ({res.status_code})")
        except Exception as e:
            print(f"❌ Unsplash 처리 중 에러: {e}")
    else:
        print("⚠️ Unsplash API 키가 설정되지 않았습니다.")

    # --- 3단계: 최후의 수단 (랜덤 이미지) ---
    print("🎨 모든 시도 실패. 랜덤 이미지를 사용합니다.")
    return "https://picsum.photos/1280/720"