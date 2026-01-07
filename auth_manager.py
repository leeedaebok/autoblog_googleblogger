import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import config  # config.py 불러오기

def get_blog_service():
    """구글 블로거 서비스 객체를 생성하여 반환"""
    creds = None
    
    # 1. 토큰 파일 확인
    if os.path.exists(config.TOKEN_FILE):
        with open(config.TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # 2. 토큰 유효성 검사 및 갱신/신규 발급
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 토큰을 갱신합니다...")
            creds.refresh(Request())
        else:
            print("🌐 새 로그인이 필요합니다...")
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CLIENT_SECRET_FILE, config.SCOPES)
            creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
        
        # 새 토큰 저장
        with open(config.TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('blogger', 'v3', credentials=creds)