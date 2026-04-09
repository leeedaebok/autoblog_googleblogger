import json
import requests
import google.oauth2.service_account
import google.auth.transport.requests
import config

def test_indexing_v3(target_url):
    # 1. 최신 가이드라인에 따른 v3 엔드포인트 설정
    # 가이드라인 이미지에 명시된 주소를 그대로 사용합니다.
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    
    # 2. 인증 정보 로드
    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    credentials = google.oauth2.service_account.Credentials.from_service_account_file(
        config.GOOGLE_APPLICATION_CREDENTIALS, scopes=SCOPES
    )
    
    # 액세스 토큰 갱신
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    # 3. 요청 본문 구성
    payload = {
        "url": target_url,
        "type": "URL_UPDATED"
    }

    headers = {
        "Content-Type": "application/json", # 가이드라인 명시 사항
        "Authorization": f"Bearer {access_token}"
    }

    print(f"🚀 [v3] 색인 요청 시작: {target_url}")
    
    try:
        response = requests.post(ENDPOINT, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ 드디어 성공(v3)! (응답: {response.status_code})")
            print(f"결과: {response.json()}")
        else:
            print(f"❌ 실패: {response.status_code}")
            print(f"에러 메시지: {response.text}")
            
    except Exception as e:
        print(f"💥 통신 에러: {str(e)}")

if __name__ == "__main__":
    # 이사한 블로그 주소로 테스트
    sample_url = "https://bok.bokgoon.com/2026/02/ai-future-just-got-real-are-you-ready.html"
    test_indexing_v3(sample_url)