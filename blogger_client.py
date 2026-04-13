def post_article(service, data):
    """작성된 글 데이터를 블로그에 발행"""
    try:
        import config
        blog_id = config.BLOG_ID
        if not blog_id:
            print("❌ .env에 BLOG_ID가 설정되지 않았습니다.")
            return
        blog_name = "bok's back pocket"

        # 3. 글 내용 구성
        body = {
            "title": data['title'],
            "content": data['content'],
            # [수정] 태그가 없어도 에러 안 나게 안전 처리 (.get 사용)
            "labels": data.get('tags', [])
        }

        # 4. 발행 요청 (isDraft=False는 즉시 발행, True면 비공개 초안)
        posts = service.posts().insert(
            blogId=blog_id, 
            body=body, 
            isDraft=False
        ).execute()
        
        print(f"✅ 발행 완료: {posts['url']}")

        # ▼▼▼ 색인 요청 로직 추가 위치 ▼▼▼
        try:
            from indexing_manager import request_indexing
            # 발행된 포스트의 실제 URL을 전달합니다.
            indexing_success = request_indexing(posts['url'])
            if not indexing_success:
                print("⚠️ 색인 요청 실패")
        except Exception as e:
            print(f"❌ 색인 모듈 실행 중 에러: {e}")
            
    except Exception as e:
        print(f"❌ 발행 중 오류 발생: {e}")