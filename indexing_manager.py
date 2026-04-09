import json
import httplib2
from oauth2client.service_account import ServiceAccountCredentials

def request_indexing(post_url):
    """
    구글 Indexing API를 통해 URL 색인을 요청합니다. (HTTP 직접 호출 방식)
    """
    import config
    
    # 필수 스코프
    SCOPES = ["https://www.googleapis.com/auth/indexing"]
    # # API 엔드포인트
    # ENDPOINT = "https://indexing.googleapis.com/v1/urlNotifications:publish"
    # 가장 표준적인 Google Indexing API 엔드포인트입니다.
    ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    try:
        if not getattr(config, 'GOOGLE_APPLICATION_CREDENTIALS', None):
            print("⚠️ 서비스 계정 키 설정이 누락되어 색인 요청을 건너뜁니다.")
            return False

        # 1. 인증 및 HTTP 객체 생성
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            config.GOOGLE_APPLICATION_CREDENTIALS, SCOPES
        )
        http = credentials.authorize(httplib2.Http())
        
        # 2. 요청 데이터 구성
        content = {
            "url": post_url,
            "type": "URL_UPDATED"
        }
        
        # 3. API 호출
        print(f"🤖 구글 색인 요청 중: {post_url}")
        response, content = http.request(
            ENDPOINT, 
            method="POST", 
            body=json.dumps(content), 
            headers={'Content-Type': 'application/json'}
        )
        
        # 4. 결과 분석
        if response.status == 200:
            print(f"✅ 구글 색인 요청 완료! (상태: {response.status})")
            return True
        else:
            print(f"❌ 색인 요청 서버 응답 오류: {response.status} - {content.decode('utf-8')}")
            return False

    except Exception as e:
        print(f"❌ 구글 색인 최종 실패 상세: {str(e)}")
        return False