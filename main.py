import os
from flask import Flask
from config import MODEL_NAME
from config import BLOG_ID # config 파일에 BLOG_ID가 정의되어 있어야 합니다.

# 모듈 임포트
from auth_manager import get_blog_service
from ai_generator import generate_content, refine_topic_with_ai
from blogger_client import post_article
from trend_manager import get_google_trend
from image_manager import get_relevant_image_url

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Blog Bot is Running...</h1><a href='/run'>Click here to Post</a>"

@app.route("/run")
def run_process():
    # 1. 미국 뉴스 트렌드 가져오기
    raw_keyword = get_google_trend()
    
    # 2. AI로 매력적인 영어 제목 만들기
    final_topic = refine_topic_with_ai(raw_keyword)
    print(f"[{final_topic}] Starting process...")
    
    # 3. AI 글쓰기 (JSON 데이터 받기)
    blog_data = generate_content(final_topic)
    
    if not blog_data:
        return "Failed to generate content."
    
    # 2. 블로그 서비스 객체 먼저 가져오기 (이미지 업로드에 필요)
    try:
        service = get_blog_service()
    except Exception as e:
        return f"Auth Error: {e}"
    
    # 4. 이미지 생성 및 본문 삽입
    try:
        img_keyword = blog_data.get('image_keyword', final_topic)
        # image_url = get_relevant_image_url(img_keyword)
        
        print("✅ img_keyword:", img_keyword)
        print("✅ service:", service)
        print("✅ blog_id:", BLOG_ID)
        image_url = get_relevant_image_url(img_keyword, service=service, blog_id=BLOG_ID)
        
        if image_url:
            # 본문 맨 앞에 이미지 삽입
            img_tag = f"""
            <div style="text-align: center; margin-bottom: 30px;">
                <img src="{image_url}" alt="{img_keyword}" style="width: 100%; max-width: 800px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            </div>
            <br>
            """
            blog_data['content'] = img_tag + blog_data['content']
            print("✅ Blog post updated with internal Google image URL.")
            
    except Exception as e:
        print(f"❌ Image Error: {e}")
        image_url = None

    # ▼▼▼ [추가된 부분] 5. 푸터(Footer) 삽입: 댓글 유도 및 저작권 ▼▼▼
    footer = f"""
    <br><hr><br>
    <h3>🗣️ We want to hear from you!</h3>
    <p>What are your thoughts on <b>{final_topic}</b>? Do you agree with our analysis? <br>
    Drop a comment below and share your perspective! 👇</p>
    <br>
    <p style="font-size: 0.8em; color: gray; text-align: center;">
    © 2025 Daily Trends Analysis US. All Rights Reserved.<br>
    <i>This content was crafted with the assistance of AI to bring you the latest insights faster.</i>
    </p>
    """
    blog_data['content'] = blog_data['content'] + footer
    # ▲▲▲ 여기까지 ▲▲▲

    # 6. 블로그 발행
    try:
        service = get_blog_service()
        post_article(service, blog_data)
        return f"<h2>Post Successful!</h2><p>Topic: {final_topic}</p><img src='{image_url}' width='300'>"
    except Exception as e:
        return f"Publishing Error: {e}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)