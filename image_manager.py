import requests
import config

def get_relevant_image_url(query):
    """검색어(query)로 Unsplash에서 이미지 1장을 찾아 URL을 반환"""
    if not config.UNSPLASH_ACCESS_KEY:
        return None
        
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "client_id": config.UNSPLASH_ACCESS_KEY,
        "per_page": 1,
        "orientation": "landscape" # 가로 사진 선호
    }

    try:
        print(f"🖼️ '{query}' 키워드로 이미지 검색 중...")
        response = requests.get(url, params=params)
        data = response.json()

        if data['results']:
            # 첫 번째 결과의 이미지 URL 반환 (regular 사이즈)
            image_url = data['results'][0]['urls']['regular']
            print("✅ 이미지 찾기 성공!")
            return image_url
        else:
            print("⚠️ 이미지를 찾지 못했습니다.")
            return None

    except Exception as e:
        print(f"❌ 이미지 검색 실패: {e}")
        return None