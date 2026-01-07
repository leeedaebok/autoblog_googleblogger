def post_article(service, data):
    """작성된 글 데이터를 블로그에 발행"""
    try:
        # 내 블로그 정보 가져오기
        blogs = service.blogs().listByUser(userId='self').execute()
        if not blogs.get('items'):
            print("❌ 계정에 블로그가 없습니다.")
            return

        # 첫 번째 블로그 선택
        blog_id = blogs['items'][0]['id']
        blog_name = blogs['items'][0]['name']

        # 글 내용 구성
        body = {
            "title": data['title'],
            "content": data['content'],
            "labels": data['tags']
        }

        # 발행 요청
        posts = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        
        print(f"✅ 발행 성공! [{blog_name}]")
        print(f"   제목: {posts['title']}")
        print(f"   링크: {posts['url']}")
        
    except Exception as e:
        print(f"❌ 발행 중 오류 발생: {e}")