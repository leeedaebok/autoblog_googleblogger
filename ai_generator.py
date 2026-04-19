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
    You are a curious, opinionated blogger who personally dug into this topic and is sharing what you found — not an AI assistant summarizing facts.
    Topic: {topic}

    [Voice & Tone]
    - Write in first person. Use phrases like "I looked into this", "What surprised me was", "Here's what I actually found", "I used to think... but then".
    - Sound like a real person: share a personal reaction, a moment of surprise, or a mild opinion. Don't be neutral.
    - Be conversational but credible. Imagine explaining this to a smart friend over coffee — not lecturing, just sharing.
    - Use rhetorical questions to pull the reader in: "Sound familiar?", "But here's the thing —", "So why does nobody talk about this?"

    [Structure — follow this order]
    1. **Hook (1 paragraph):** Open with a striking personal observation or a counterintuitive fact that made YOU stop and think. No greetings, no "In this post I will".
    2. **📌 Key Takeaways (3 bullet points):** What the reader will walk away knowing. Place right after the hook.
    3. **The Setup — Why I Looked Into This:** One short section explaining what sparked your curiosity about this topic. Make it feel real.
    4. **What I Found (main body, 3–4 sections with <h3> headings):** Go deeper. Mix facts, examples, and your own reactions. Use "what most people don't realize is...", "the part that got me was...", "this is where it gets interesting".
    5. **The Part Everyone Gets Wrong:** One section specifically addressing a common misconception or oversimplification about this topic.
    6. **What This Actually Means For You:** Practical, direct advice or implication. Not generic — tie it specifically to the topic.
    7. **My Take:** A short closing paragraph with your honest opinion or prediction. End with a question for the reader to reflect on.

    [Formatting]
    - HTML only: <h3>, <p>, <ul>, <li>, <strong>, <em>
    - 900–1100 words total
    - Use single quotes (') inside HTML attributes and inline quotes — never double quotes (") to avoid JSON parse errors.

    [Output Schema]
    Return ONLY a valid JSON object:
    {{
        "title": "Engaging, specific title — avoid generic clickbait. Sound like a real person wrote it.",
        "meta_description": "155 characters max — written like a teaser, not a summary. Make the reader want to click.",
        "image_keyword": "Concrete visual scene for AI image generation (not abstract)",
        "content": "Full HTML content",
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
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