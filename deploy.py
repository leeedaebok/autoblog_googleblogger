import os
import subprocess
import sys

# === [설정] ===
SERVICE_NAME = "autoblogger-service"
REGION = "asia-northeast3"
# =============

def deploy():
    print(f"[{SERVICE_NAME}] 배포 준비 중...")
    
    # 1. .env 파일 읽어서 문자열로 합치기
    env_list = []
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # 주석(#)이거나 빈 줄이면 패스
                    if not line or line.startswith("#"):
                        continue
                    env_list.append(line)
        except Exception as e:
            print(f"[오류] .env 파일을 읽는 중 에러 발생: {e}")
            return
    else:
        print("[오류] .env 파일이 없습니다!")
        return

    if not env_list:
        print("[오류] .env 파일에 유효한 내용이 없습니다.")
        return

    # 리스트를 콤마로 연결 (KEY=VAL,KEY2=VAL2...)
    env_vars_string = ",".join(env_list)
    print(f"[확인] {len(env_list)}개의 환경 변수를 로드했습니다.")

    # 2. gcloud 배포 명령어 실행
    # (파이썬이 알아서 따옴표/띄어쓰기 처리를 해줍니다)
    cmd = [
        "gcloud", "run", "deploy", SERVICE_NAME,
        "--source", ".",
        "--region", REGION,
        "--set-env-vars", env_vars_string,
        "--allow-unauthenticated"
    ]

    print("\n[배포 시작] 구글 클라우드로 전송합니다... (1~2분 소요)")
    
    # 윈도우에서는 shell=True가 필요할 수 있음
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("\n[성공] 배포가 완료되었습니다! 위 URL을 확인하세요.")
    else:
        print("\n[실패] 배포 중 에러가 발생했습니다.")

if __name__ == "__main__":
    deploy()