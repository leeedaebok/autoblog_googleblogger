def post_article(service, data):
    """작성된 글 데이터를 블로그에 발행"""
    try:
        # 1. 내 계정의 블로그 리스트 가져오기
        blogs = service.blogs().listByUser(userId='self').execute()
        
        if not blogs.get('items'):
            print("❌ 계정에 블로그가 없습니다. 구글 블로거를 먼저 생성해주세요.")
            return

        # 2. 첫 번째 블로그 선택 (일반적으로 메인 블로그)
        # 만약 특정 블로그에만 쓰고 싶다면 blog_id = '12345678...' 처럼 직접 넣어도 됩니다.
        blog_id = blogs['items'][0]['id']
        blog_name = blogs['items'][0]['name']

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