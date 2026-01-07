from auth_manager import get_blog_service
from ai_generator import generate_content
from blogger_client import post_article
# ▼ 추가된 부분
from image_manager import get_relevant_image_url

TOPIC = "주말에 집에서 즐기는 취미 생활 추천 5가지"

def main():
    # 1. AI 글쓰기 요청 (키워드도 같이 받아옴)
    blog_data = generate_content(TOPIC)
    
    if blog_data:
        # ▼▼▼ 이미지 처리 로직 추가 ▼▼▼
        keyword = blog_data.get('image_keyword')
        if keyword:
            image_url = get_relevant_image_url(keyword)
            if image_url:
                # 본문 맨 앞에 이미지 태그 삽입 (스타일 적용)
                img_tag = f'<img src="{image_url}" alt="{keyword}" style="width:100%; height:auto; margin-bottom:30px; border-radius:10px;">'
                blog_data['content'] = img_tag + blog_data['content']
        # ▲▲▲ 여기까지 ▲▲▲

        # 2. 구글 인증 및 서비스 연결
        service = get_blog_service()
        
        # 3. 블로그 발행
        post_article(service, blog_data)
    else:
        print("시스템을 종료합니다.")

if __name__ == "__main__":
    main()