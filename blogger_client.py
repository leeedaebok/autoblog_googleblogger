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

        print(f"📝 블로그 선택됨: {blog_name}")

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
        
        print(f"✅ 발행 성공! [{blog_name}]")
        print(f"   제목: {posts['title']}")
        print(f"   링크: {posts['url']}")
        print(f"   태그(라벨): {body['labels']}")

        # ▼▼▼ 색인 요청 로직 추가 위치 ▼▼▼
        try:
            from indexing_manager import request_indexing
            # 발행된 포스트의 실제 URL을 전달합니다.
            indexing_success = request_indexing(posts['url'])
            if indexing_success:
                print("🚀 구글 서치 콘솔에 즉시 색인 요청을 보냈습니다.")
            else:
                print("⚠️ 색인 요청 과정에서 문제가 발생했습니다.")
        except Exception as e:
            print(f"❌ 색인 모듈 실행 중 에러: {e}")
            
    except Exception as e:
        print(f"❌ 발행 중 오류 발생: {e}")