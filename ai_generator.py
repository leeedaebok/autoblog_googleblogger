import json
import re
from google import genai
from google.genai import types
import config
from config import MODEL_NAME

# Gemini 클라이언트 초기화
client = genai.Client(api_key=config.GEMINI_API_KEY)

def clean_json_text(text):
    """
    AI가 생성한 텍스트에서 JSON 파싱을 방해하는 요소를 제거합니다.
    """
    # 1. 제어 문자(줄바꿈 제외) 제거
    text = re.sub(r'[\x00-\x1F\x7F]', '', text)
    # 2. Markdown 코드 블록 기호 제거 (있을 경우)
    text = text.replace('```json', '').replace('```', '').strip()

    # 마지막이 }로 끝나지 않으면 강제로 닫아주는 시도
    if not text.endswith('}'):
        text += '"}'
        
    return text

def generate_content(topic):
    """
    주제(topic)를 받아서 미국 타겟의 분석 영어 블로그 포스팅 내용을 JSON으로 반환
    """
    
    # [가이드라인] 본문 내 큰따옴표 사용을 자제시키거나 escape 처리를 유도합니다.
    prompt = f"""
    You are a professional columnist and trend analyst targeting a US audience.
    Topic: {topic}

    [Writing Guidelines]
    1. **Hook:** Start with a provocative question or strong statement.
    2. **Structure:** MUST include "📌 Key Takeaways" (3 bullet points) at the beginning.
    3. **Content:** Long-form HTML (<h3>, <p>, <ul>, <li>). 1000+ words.
    4. **Safety:** Inside the "content" string, use single quotes (') for quotes or titles instead of double quotes (") to avoid JSON errors.
    5. Content Length: Aim for 800-1000 words to ensure the JSON structure is not cut off.
    6. Special Characters: Do not use double quotes (") inside the HTML tags; use single quotes (') instead.

    [Output Schema]
    Return ONLY a valid JSON object:
    {{
        "title": "Catchy Title",
        "image_keyword": "Abstract keyword for AI image generation",
        "content": "Full HTML content",
        "tags": ["tag1", "tag2", "tag3"]
    }}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        raw_text = response.text
        
        # 데이터 정제 실행
        refined_text = clean_json_text(raw_text)
        
        return json.loads(refined_text)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 파싱 실패: {e} | 원본 앞부분: {raw_text[:100]}")
        return None
    except Exception as e:
        print(f"❌ AI 생성 실패: {e}")
        return None

def refine_topic_with_ai(keyword):
    """
    단순 키워드를 블로그 포스팅용 매력적인 영어 제목으로 변환
    """
    try:
        prompt = f"""
        Keyword: '{keyword}'
        Create ONE catchy blog post title based on this keyword.
        Output only the title text. No quotes.
        """
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
        new_topic = response.text.strip()
        return new_topic

    except Exception as e:
        print(f"❌ 제목 개선 실패: {e}")
        return f"Everything about {keyword}"