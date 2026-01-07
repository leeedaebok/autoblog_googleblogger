import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# ▼ 추가된 부분
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

if not GEMINI_API_KEY:
    raise ValueError("❌ .env 파일에서 GEMINI_API_KEY를 찾을 수 없습니다.")
# ▼ 추가된 부분
if not UNSPLASH_ACCESS_KEY:
    print("⚠️ 경고: .env에서 UNSPLASH_ACCESS_KEY를 찾지 못했습니다. 이미지 기능이 작동하지 않습니다.")

CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.pickle'
SCOPES = ['https://www.googleapis.com/auth/blogger']
MODEL_NAME = 'gemini-2.0-flash'