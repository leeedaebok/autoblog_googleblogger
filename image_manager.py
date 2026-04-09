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

            response = requests.get(pollinations_url, timeout=40)

            if response.status_code == 200:
                return pollinations_url

            print(f"⚠️ 이미지 생성 재시도 ({attempt+1}/3): 응답 {response.status_code}")
            time.sleep(wait_sec)

        except Exception as e:
            print(f"❌ 이미지 생성 오류: {e}")
            time.sleep(wait_sec)

    # --- 2단계: Unsplash 백업 ---
    print("⚠️ Pollinations 실패 → Unsplash 시도")
    access_key = getattr(config, 'UNSPLASH_ACCESS_KEY', None)

    if access_key:
        try:
            search_url = f"https://api.unsplash.com/photos/random?query={keyword}&orientation=landscape&client_id={access_key}"
            res = requests.get(search_url, timeout=10)
            if res.status_code == 200:
                return res.json()['urls']['regular']
            else:
                print(f"❌ Unsplash 실패: {res.status_code}")
        except Exception as e:
            print(f"❌ Unsplash 오류: {e}")
    else:
        print("❌ UNSPLASH_ACCESS_KEY 미설정")

    # --- 3단계: 랜덤 이미지 ---
    print("⚠️ 이미지 확보 실패 → 랜덤 이미지 사용")
    return "https://picsum.photos/1280/720"