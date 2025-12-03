# rag/llm.py
import os
import google.generativeai as genai
from typing import List, Dict, Any

# .env에서 API 키 로드
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_answer(query: str, docs: List[Dict[str, Any]]) -> str:
    """
    검색된 문서(docs)를 바탕으로 Gemini가 답변을 생성합니다.
    """
    if not GEMINI_API_KEY:
        return "오류: .env 파일에 GEMINI_API_KEY가 설정되지 않았습니다."

    # 문맥(Context) 구성
    context_text = ""
    for i, doc in enumerate(docs, 1):
        meta = doc.get('metadata', {})
        date = meta.get('date', '날짜미상')
        title = meta.get('title', '제목없음')
        
        # [수정] 링크(URL) 정보를 Gemini에게도 알려줍니다.
        # doc['id']가 곧 링크 URL입니다.
        link = doc.get('id', '') 
        
        content = doc.get('text', '')
        
        # 문맥에 (제목, 날짜, URL)을 명확히 넣어줍니다.
        context_text += f"\n[문서 {i}] 날짜: {date} | 제목: {title} | 링크: {link}\n내용:\n{content}\n" + "-"*30

    # 시스템 프롬프트 (최신성 + 링크 강조)
    prompt = f"""
당신은 숭실대학교 학사 정보를 안내하는 똑똑한 AI 조교입니다.
아래 제공된 [검색된 문서들]을 바탕으로 사용자의 질문에 답변하세요.

**[답변 작성 원칙]**
1. **최신 정보 우선**: 문서의 '날짜'를 확인하여 가장 최신 정보를 정답으로 간주하세요. (2025년 정보를 2022년 정보보다 우선시할 것)
2. **링크 포함**: 답변 중에 관련 공지사항을 언급할 때는 반드시 **마크다운 링크 형식**을 사용하세요.
   - 예시: 자세한 내용은 [2025학년도 전과 안내](https://sw.ssu.ac.kr/...)를 참고하세요.
3. **근거 기반**: 문서에 없는 내용은 지어내지 말고 "정보가 부족합니다"라고 하세요.
4. **출처 명시**: 답변 끝부분에 '참고 문서' 섹션을 만들 필요는 없습니다. (UI에서 따로 보여줄 것입니다)
5. **친절함**: 학생에게 말하듯 명확하고 친절하게 설명하세요.

**[검색된 문서들]**
{context_text}

**[사용자 질문]**
{query}

**[답변]**
"""

    try:
        # 2.0 Flash 모델 사용
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return f"죄송합니다. 답변 생성 중 오류가 발생했습니다: {e}"