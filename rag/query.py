# rag/query.py
from __future__ import annotations
from typing import List, Dict, Any
from .ranking import retrieve_top_k_for_rag

def _expand_query_terms(query: str) -> str:
    """
    [쿼리 확장]
    사용자가 '학과'로 검색하면 '학부'도 추가하고,
    '학부'로 검색하면 '학과'도 추가해서 검색 확률을 높임.
    예: "소프트웨어학과 전과" -> "소프트웨어학과 소프트웨어학부 전과"
    """
    expanded = query
    
    # '학과'가 있으면 '학부'라는 단어도 슬쩍 끼워넣음
    if "학과" in query:
        # 단순 치환이 아니라 뒤에 이어붙여서 원본 의미도 보존
        expanded += " " + query.replace("학과", "학부")
        
    # '학부'가 있으면 '학과'라는 단어도 슬쩍 끼워넣음
    elif "학부" in query:
        expanded += " " + query.replace("학부", "학과")
        
    return expanded

def rag_search(
    query_text: str, 
    top_k: int = 10  # LLM에게 넘겨줄 최종 문서 개수 (7 -> 10 추천)
) -> List[Dict[str, Any]]:
    """
    RAG 검색: Chroma + BM25 + 최신성 + RRF
    """
    # 1. 쿼리 확장 수행 (학과 <-> 학부 상호보완)
    final_query = _expand_query_terms(query_text)
    
    # 로그로 확인하고 싶으면 아래 주석 해제
    # print(f"[QUERY EXPANSION] '{query_text}' -> '{final_query}'")

    # 2. 확장된 쿼리로 검색 수행
    # 후보군(chroma_top_n, bm25_top_n)은 100개로 넉넉하게 잡음
    docs = retrieve_top_k_for_rag(
        final_query, 
        k=top_k,
        chroma_top_n=100, 
        bm25_top_n=100
    )
    return docs