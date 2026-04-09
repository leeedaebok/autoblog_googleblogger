import os
import pickle
import logging
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
import config  # config.py 불러오기

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_blog_service():
    """구글 블로거 서비스 객체를 생성하여 반환 (서버 전용 수정판)"""
    creds = None
    
    # 1. 토큰 파일 로드
    if os.path.exists(config.TOKEN_FILE):
        try:
            with open(config.TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            logger.error(f"파일 읽기 오류: {e}")
            return None

    # 2. 토큰 유효성 검사 및 갱신
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("🔄 토큰 만료됨. 갱신을 시도합니다...")
            try:
                # Request 객체 생성 (기본 타임아웃 적용)
                creds.refresh(Request())
                logger.info("✅ 토큰 갱신 성공.")
            except RefreshError:
                logger.error("❌ 토큰 갱신 실패 (Refresh Token 만료/취소됨).")
                logger.error("👉 로컬 PC에서 다시 로그인하여 새 토큰 파일을 서버에 올려주세요.")
                # 잘못된 토큰 파일 삭제 (무한 루프 방지)
                if os.path.exists(config.TOKEN_FILE):
                    os.remove(config.TOKEN_FILE)
                return None
            except Exception as e:
                logger.error(f"❌ 알 수 없는 오류로 토큰 갱신 실패: {e}")
                return None
        else:
            # 서버에서는 브라우저 로그인을 할 수 없으므로 바로 에러 처리
            logger.error("⛔ 유효한 토큰이 없습니다. (서버에서는 브라우저 로그인 불가)")
            logger.error("👉 로컬에서 생성한 pickle 파일을 서버에 업로드하세요.")
            return None
        
        # 3. 갱신된 토큰 저장
        try:
            with open(config.TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        except Exception as e:
             logger.error(f"⚠️ 토큰 파일 저장 실패 (권한 문제 등): {e}")

    return build('blogger', 'v3', credentials=creds, static_discovery=False)