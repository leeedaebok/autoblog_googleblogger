# 파일명: get_token.py
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
import config  # 설정 파일 불러오기

def create_token():
    # 1. 기존 토큰이 있다면 삭제 (깨끗하게 새로 받기 위함)
    if os.path.exists(config.TOKEN_FILE):
        os.remove(config.TOKEN_FILE)
        print(f"🗑️ 기존 {config.TOKEN_FILE} 삭제 완료.")

    # 2. 브라우저 인증 시작
    print("🌐 브라우저가 열리면 구글 계정으로 로그인해주세요...")
    
    # client_secret.json 경로가 맞는지 꼭 확인하세요
    flow = InstalledAppFlow.from_client_secrets_file(
        config.CLIENT_SECRET_FILE, config.SCOPES)
    
    # 여기서 브라우저가 열립니다
    creds = flow.run_local_server(port=8080)

    # 3. 새 토큰 파일 저장
    with open(config.TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)
    
    print(f"✅ 새로운 토큰 파일 생성 완료: {config.TOKEN_FILE}")
    print("👉 이 파일을 서버의 같은 경로로 업로드하세요.")

if __name__ == "__main__":
    create_token()