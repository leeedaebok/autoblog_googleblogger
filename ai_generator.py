import json
import google.generativeai as genai
import config

# Gemini 설정
genai.configure(api_key=config.GEMINI_API_KEY)

# ★ 핵심 변경점: generation_config로 JSON 응답 강제 설정
model = genai.GenerativeModel(
    config.MODEL_NAME,
    generation_config={"response_mime_type": "application/json"}
)

# ... 상단 import 부분 동일 ...

def generate_content(topic):
    print(f"🤖 AI가 '{topic}' 주제로 글을 작성 중입니다...")
    
    prompt = f"""
    당신은 전문 블로거입니다. 아래 주제로 블로그 글을 작성해주세요.
    
    주제: {topic}

    [출력 스키마]
    반드시 아래 JSON 구조에 맞춰서 작성하세요:
    {{
        "title": "문자열 (매력적인 제목)",
        "image_keyword": "문자열 (이 글을 대표하는 영어 단어 1~2개, 예: office desk)",
        "content": "문자열 (HTML 태그 <h3>, <p>, <ul>, <li>, <b> 등을 포함한 1500자 이상의 긴 본문)",
        "tags": ["문자열1", "문자열2", "문자열3"]
    }}
    # ... 아래 조건 부분 동일 ...
    
    조건:
    1. 독자에게 친절한 해요체를 사용할 것.
    2. 전문적이고 유익한 내용을 담을 것.
    """

    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # JSON 모드를 켰으므로 마크다운 제거나 복잡한 처리가 필요 없습니다.
        # 바로 변환만 하면 됩니다.
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 변환 실패 (내용이 잘렸을 수 있음): {e}")
        return None
    except Exception as e:
        print(f"❌ AI 생성 실패: {e}")
        return None