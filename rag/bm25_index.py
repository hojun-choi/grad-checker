# rag/bm25_index.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional

import re
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi

from .config import SSU_NOTICES_CSV_PATH


_TOKEN_SPLIT_RE = re.compile(r"\W+", flags=re.UNICODE)


def _tokenize(text: str) -> List[str]:
    """
    매우 단순한 토크나이저.
    - 한/영/숫자 섞인 문장을 공백 + 기호 기준으로 잘라서 토큰 리스트로 변환.
    나중에 원하면 Mecab, khaiii 등으로 교체 가능.
    """
    text = text.lower()
    tokens = [t for t in _TOKEN_SPLIT_RE.split(text) if t]
    return tokens


@dataclass
class BM25Document:
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    tokens: List[str]


class BM25Index:
    def __init__(self, csv_path: str):
        self.csv_path = Path(csv_path)
        self.documents: List[BM25Document] = []
        self._bm25: Optional[BM25Okapi] = None

        self._load_from_csv()

    def _load_from_csv(self) -> None:
        """
        notices/ssu_notices.csv 전체를 로드해서 BM25 코퍼스 구성.
        """
        if not self.csv_path.exists():
            print(f"[BM25] CSV not found: {self.csv_path}")
            return

        df = pd.read_csv(self.csv_path)

        docs: List[BM25Document] = []
        for _, row in df.iterrows():
            try:
                department = row.get("department", "")
                title = row.get("title", "")
                author = row.get("author", "")
                date_str = row.get("date", "")
                link = row.get("link", "")
                content = row.get("content", "")
                views = row.get("views", "")

                # 실제 검색에 사용할 텍스트
                text = f"{title}\n\n{content}"

                # 메타데이터 (timestamp는 나중에 indexing.py에서 채워줄 예정)
                metadata: Dict[str, Any] = {
                    "department": department,
                    "title": title,
                    "author": author,
                    "date": date_str,
                    "link": link,
                    "views": views,
                }

                doc_id = str(link) or f"row-{_}"
                tokens = _tokenize(text)

                docs.append(
                    BM25Document(
                        doc_id=doc_id,
                        text=text,
                        metadata=metadata,
                        tokens=tokens,
                    )
                )
            except Exception as e:
                print(f"[BM25] row {_} parse error: {e}")

        self.documents = docs
        corpus = [d.tokens for d in self.documents]
        if corpus:
            self._bm25 = BM25Okapi(corpus)
            print(f"[BM25] Loaded {len(self.documents)} documents from CSV.")
        else:
            print("[BM25] No documents to index.")

    def rebuild(self) -> None:
        """
        CSV 변경(크롤링 후) 이후에 BM25 코퍼스를 다시 만들고 싶을 때 사용.
        (추후 /internal/crawl-and-index 끝에서 호출하면 됨)
        """
        self._load_from_csv()

    def search(self, query: str, top_k: int = 20) -> List[Dict[str, Any]]:
        """
        BM25 Top-k 검색.
        반환 형식: 각 원소는 {id, text, metadata, score}
        """
        if self._bm25 is None or not self.documents:
            return []

        q_tokens = _tokenize(query)
        scores = self._bm25.get_scores(q_tokens)

        # (score, idx) 튜플로 정렬
        scored_indices = sorted(
            [(s, i) for i, s in enumerate(scores)],
            key=lambda x: x[0],
            reverse=True,
        )[:top_k]

        results: List[Dict[str, Any]] = []
        for score, idx in scored_indices:
            doc = self.documents[idx]
            result = {
                "id": doc.doc_id,
                "text": doc.text,
                "metadata": doc.metadata,
                "score": float(score),
            }
            results.append(result)

        return results


# 전역 싱글톤
_bm25_index: Optional[BM25Index] = None


def get_bm25_index() -> BM25Index:
    global _bm25_index
    if _bm25_index is None:
        _bm25_index = BM25Index(SSU_NOTICES_CSV_PATH)
    return _bm25_index


def bm25_search(query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    index = get_bm25_index()
    return index.search(query, top_k=top_k)


def bm25_rebuild() -> None:
    index = get_bm25_index()
    index.rebuild()
