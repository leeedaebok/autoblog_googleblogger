import os
import sys
import traceback
from datetime import datetime

# 스크립트 위치 기준으로 작업 디렉토리 설정
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def setup_logs():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return log_dir, ts


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()

    def flush(self):
        for s in self.streams:
            s.flush()


def run():
    log_dir, ts = setup_logs()
    log_path = os.path.join(log_dir, f'{ts}.txt')
    error_path = os.path.join(log_dir, f'{ts}_error.txt')

    error_occurred = False
    error_msg = ""

    with open(log_path, 'w', encoding='utf-8') as log_f:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = Tee(old_stdout, log_f)
        sys.stderr = Tee(old_stderr, log_f)

        try:
            print(f"[{ts}] autoblog_googleblogger 실행 시작")

            from config import BLOG_ID
            from auth_manager import get_blog_service
            from ai_generator import generate_content, refine_topic_with_ai
            from blogger_client import post_article
            from trend_manager import get_google_trend
            from image_manager import get_relevant_image_url

            # 1. 트렌드 키워드 가져오기
            raw_keyword = get_google_trend()

            # 2. AI 제목 생성
            final_topic = refine_topic_with_ai(raw_keyword)
            print(f"[{final_topic}] Starting process...")

            # 3. 콘텐츠 생성
            blog_data = generate_content(final_topic)
            if not blog_data:
                print("Failed to generate content.")
                return

            # 4. 블로그 서비스 인증
            service = get_blog_service()

            # 5. 이미지 삽입
            try:
                img_keyword = blog_data.get('image_keyword', final_topic)
                image_url = get_relevant_image_url(img_keyword, service=service, blog_id=BLOG_ID)
                if image_url:
                    img_tag = (
                        f'<div style="text-align: center; margin-bottom: 30px;">'
                        f'<img src="{image_url}" alt="{img_keyword}" '
                        f'style="width: 100%; max-width: 800px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                        f'</div><br>'
                    )
                    blog_data['content'] = img_tag + blog_data['content']
                    print(f"✅ 이미지 삽입 완료: {image_url}")
            except Exception as e:
                print(f"❌ Image Error: {e}")

            # 6. 푸터 삽입
            footer = (
                f'<br><hr><br>'
                f'<h3>🗣️ We want to hear from you!</h3>'
                f'<p>What are your thoughts on <b>{final_topic}</b>? '
                f'Do you agree with our analysis?<br>'
                f'Drop a comment below and share your perspective! 👇</p>'
                f'<br>'
                f'<p style="font-size: 0.8em; color: gray; text-align: center;">'
                f'© 2025 Daily Trends Analysis US. All Rights Reserved.<br>'
                f'<i>This content was crafted with the assistance of AI to bring you the latest insights faster.</i>'
                f'</p>'
            )
            blog_data['content'] += footer

            # 7. 발행
            post_article(service, blog_data)
            print(f"✅ Post Successful! Topic: {final_topic}")

        except Exception:
            error_occurred = True
            error_msg = traceback.format_exc()
            print(f"❌ 오류 발생:\n{error_msg}")
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    if error_occurred:
        with open(error_path, 'w', encoding='utf-8') as ef:
            ef.write(error_msg)
        print(f"❌ 에러 로그 저장: {error_path}")


if __name__ == '__main__':
    run()
