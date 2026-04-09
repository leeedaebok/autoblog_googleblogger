import os
import sys
import traceback
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PROJECT_NAME = "autoblog_googleblogger"


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

    error_occurred = False
    error_msg = ""

    with open(log_path, 'w', encoding='utf-8') as log_f:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = Tee(old_stdout, log_f)
        sys.stderr = Tee(old_stderr, log_f)

        try:
            print(f"[{ts}] {PROJECT_NAME} 실행 시작")

            from config import BLOG_ID
            from auth_manager import get_blog_service
            from ai_generator import generate_content, refine_topic_with_ai
            from blogger_client import post_article
            from trend_manager import get_google_trend
            from image_manager import get_relevant_image_url

            raw_keyword = get_google_trend()
            final_topic = refine_topic_with_ai(raw_keyword)
            print(f"[{final_topic}] Starting process...")

            blog_data = generate_content(final_topic)
            if not blog_data:
                raise RuntimeError("Failed to generate content.")

            service = get_blog_service()

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
            except Exception as e:
                print(f"❌ Image Error: {e}")

            footer = (
                f'<br><hr><br>'
                f'<h3>🗣️ We want to hear from you!</h3>'
                f'<p>What are your thoughts on <b>{final_topic}</b>? Drop a comment below! 👇</p>'
                f'<p style="font-size: 0.8em; color: gray; text-align: center;">'
                f'© 2025 Daily Trends Analysis US. All Rights Reserved.<br>'
                f'<i>This content was crafted with the assistance of AI.</i></p>'
            )
            blog_data['content'] += footer

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
        # 에러 로그 보존 후 메일 발송
        error_path = os.path.join(log_dir, f'{ts}_error.txt')
        os.rename(log_path, error_path)
        with open(error_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        from notify import send_error_email
        send_error_email(PROJECT_NAME, log_content)
    else:
        # 정상 종료 시 로그 삭제
        os.remove(log_path)


if __name__ == '__main__':
    run()
