import base64

# token.pickle 파일을 읽어서 문자열로 변환
try:
    with open("token.pickle", "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode('utf-8')
    print("=== 아래 내용을 모두 복사하세요 (시작) ===")
    print(encoded_string)
    print("=== 위 내용을 모두 복사하세요 (끝) ===")
except FileNotFoundError:
    print("❌ token.pickle 파일이 없습니다. 먼저 한 번 로그인을 진행해주세요.")