# rag/indexing.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import pandas as pd

from .config import SSU_NOTICES_CSV_PATH
from .chroma_client import add_documents
from .bm25_index import bm25_rebuild


def _parse_timestamp(date_str: str) -> Optional[int]:
    """
    CSV의 date 문자열을 epoch timestamp(int)로 변환.
    형식이 안 맞으면 None.
    """
    if date_str is None:
        return None

    s = str(date_str).strip()
    if not s:
        return None

    candidates = [
        "%Y-%m-%d",
        "%Y.%m.%d",
        "%Y/%m/%d",
        "%Y-%m-%d %H:%M",
        "%Y.%m.%d %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(s, fmt)
            return int(dt.timestamp())
        except ValueError:
            continue

    return None


def _build_metadata(row: pd.Series) -> Dict[str, Any]:
    """
    한 행(row)에서 Chroma에 넣을 metadata 딕셔너리 생성.
    """
    department = row.get("department", "")
    title = row.get("title", "")
    author = row.get("author", "")
    date_str = row.get("date", "")
    link = row.get("link", "")
    views = row.get("views", "")

    ts = _parse_timestamp(date_str)
    ts_val = int(ts) if ts is not None else 0

    metadata: Dict[str, Any] = {
        "department": str(department) if department is not None else "",
        "title": str(title) if title is not None else "",
        "author": str(author) if author is not None else "",
        "date": str(date_str) if date_str is not None else "",
        "timestamp": ts_val,
        "link": str(link) if link is not None else "",
        "views": str(views) if views is not None else "",
    }
    return metadata


def backfill_from_csv(
    csv_path: Optional[str] = None,
    batch_size: int = 256,
) -> int:
    """
    전체 CSV(notices/ssu_notices.csv)를 읽어서
    Chroma 컬렉션에 upsert 방식으로 전부 넣는다.
    반환값: 인덱싱된 문서 개수
    """
    if csv_path is None:
        csv_path = SSU_NOTICES_CSV_PATH

    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"[INDEX] CSV not found: {csv_file}")
        return 0

    print(f"[INDEX] Loading CSV: {csv_file}")
    df = pd.read_csv(csv_file)
    if df.empty:
        print("[INDEX] CSV is empty, nothing to index.")
        return 0

    df = df.fillna("")

    ids: List[str] = []
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        title = row.get("title", "")
        content = row.get("content", "")
        link = row.get("link", "")
        doc_id = str(link).strip() if str(link).strip() else f"row-{idx}"

        text = f"{title}\n\n{content}"
        meta = _build_metadata(row)

        ids.append(doc_id)
        texts.append(text)
        metadatas.append(meta)

    total = len(ids)
    print(f"[INDEX] Start indexing {total} documents into Chroma...")

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch_ids = ids[start:end]
        batch_texts = texts[start:end]
        batch_metas = metadatas[start:end]

        add_documents(batch_ids, batch_texts, batch_metas)
        print(f"[INDEX] Indexed {end}/{total} documents...")

    print(f"[INDEX] Done. Total indexed: {total}")
    return total

# [새로 추가할 함수]
def update_incremental(new_data_list: List[Dict[str, Any]]) -> int:
    """
    크롤러가 방금 수집한 '새로운 데이터(List[dict])'만 받아서
    ChromaDB에 추가하고, BM25 인덱스만 갱신하는 함수.
    (전체 CSV를 다시 읽거나 전체 임베딩을 하지 않음)
    """
    if not new_data_list:
        return 0

    print(f"[INDEX] Incremental update started. New docs: {len(new_data_list)}")

    # List[dict] -> DataFrame 변환 (기존 _build_metadata 로직 재사용을 위해)
    df = pd.DataFrame(new_data_list).fillna("")

    ids: List[str] = []
    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        title = row.get("title", "")
        content = row.get("content", "")
        link = row.get("link", "")
        
        # ID 생성
        doc_id = str(link).strip() if str(link).strip() else f"new-{idx}"

        # 검색용 텍스트
        text = f"{title}\n\n{content}"
        
        # 메타데이터 생성 (기존 함수 재사용)
        meta = _build_metadata(row)

        ids.append(doc_id)
        texts.append(text)
        metadatas.append(meta)

    # 1. ChromaDB에 '새로운 것만' 추가 (임베딩 비용 절약)
    add_documents(ids, texts, metadatas)
    print(f"[INDEX] Successfully added {len(ids)} new documents to Chroma.")

    # 2. BM25는 전체 통계(IDF)가 중요하고 생성 속도가 빠르므로 전체 재빌드 (CSV 기준)
    #    (CSV는 이미 main.py에서 업데이트 되었음)
    print("[INDEX] Rebuilding BM25 index to reflect new data...")
    bm25_rebuild()
    
    return len(ids)

def reindex_all(csv_path: Optional[str] = None) -> int:
    """
    1) CSV 전체를 Chroma에 백필(backfill)
    2) BM25 인덱스 재빌드
    """
    count = backfill_from_csv(csv_path=csv_path)
    print("[INDEX] Rebuilding BM25 index from CSV...")
    bm25_rebuild()
    print("[INDEX] BM25 rebuild done.")
    return count
