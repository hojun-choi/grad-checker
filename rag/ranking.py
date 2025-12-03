# rag/ranking.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from datetime import datetime, timezone
import math

from .chroma_client import query as chroma_query
from .bm25_index import bm25_search


@dataclass
class RankedDoc:
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    base_score: float        # 검색 유사도 점수
    recency_score: float     # 최신성 점수 (0~1)
    combined_score: float    # 결합 점수


def _now_ts() -> float:
    return datetime.now(tz=timezone.utc).timestamp()


def _compute_recency_score(
    timestamp: float | None,
    now_ts: float | None = None,
    half_life_days: float = 365.0,  # [수정] 30일 -> 365일 (1년 지나면 점수 절반)
) -> float:
    if timestamp is None or timestamp <= 0:
        return 0.0

    if now_ts is None:
        now_ts = _now_ts()

    age_seconds = max(0.0, now_ts - float(timestamp))
    age_days = age_seconds / 86400.0

    if age_days <= 0:
        return 1.0

    # 지수 감쇠 계산
    lam = math.log(2.0) / half_life_days
    score = math.exp(-lam * age_days)
    return float(score)


def _min_max_normalize(scores: List[float]) -> List[float]:
    if not scores:
        return []
    s_min = min(scores)
    s_max = max(scores)
    if s_max == s_min:
        return [1.0 for _ in scores]
    return [(s - s_min) / (s_max - s_min) for s in scores]


def _build_ranked_list_for_system(
    system_name: str,
    raw_results: List[Dict[str, Any]],
    is_distance_score: bool = False,
    similarity_from_distance: bool = True,
) -> List[RankedDoc]:
    now_ts = _now_ts()
    base_scores: List[float] = []

    # 1. Base Score 추출
    for r in raw_results:
        if is_distance_score:
            dist = float(r.get("distance", 0.0))
            if similarity_from_distance:
                base = 1.0 / (1.0 + dist)
            else:
                base = -dist
        else:
            base = float(r.get("score", 0.0))
        base_scores.append(base)

    # 2. Base Score 정규화 (0~1)
    base_norm = _min_max_normalize(base_scores)

    ranked_docs: List[RankedDoc] = []
    for r, b_norm in zip(raw_results, base_norm):
        meta = r.get("metadata", {}) or {}
        ts = meta.get("timestamp", None)
        try:
            ts = float(ts) if ts is not None else None
        except Exception:
            ts = None

        rec = _compute_recency_score(ts, now_ts=now_ts)

        # [수정] 최신성 가중치 20%로 상향 (기존 0.05 -> 0.20)
        # 키워드가 조금 덜 맞아도 최신 글이 상위권에 오르게 됨
        combined = 0.80 * b_norm + 0.20 * rec

        ranked_docs.append(
            RankedDoc(
                doc_id=str(r.get("id")),
                text=str(r.get("text", "")),
                metadata=meta,
                base_score=b_norm,
                recency_score=rec,
                combined_score=combined,
            )
        )

    # Combined Score 기준으로 정렬
    ranked_docs.sort(key=lambda d: d.combined_score, reverse=True)
    return ranked_docs


def _rrf_fusion(
    ranked_lists: Dict[str, List[RankedDoc]],
    top_k: int = 7,
    k: int = 60,
) -> List[Tuple[RankedDoc, float]]:
    aggregated: Dict[str, Tuple[RankedDoc, float]] = {}

    for system_name, docs in ranked_lists.items():
        for rank_idx, doc in enumerate(docs, start=1):
            contrib = 1.0 / (k + rank_idx)
            if doc.doc_id not in aggregated:
                aggregated[doc.doc_id] = (doc, contrib)
            else:
                prev_doc, prev_score = aggregated[doc.doc_id]
                aggregated[doc.doc_id] = (prev_doc, prev_score + contrib)

    items = list(aggregated.values())
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top_k]


def retrieve_top_k_for_rag(
    query_text: str,
    k: int = 7,
    chroma_top_n: int = 20,
    bm25_top_n: int = 20,
) -> List[Dict[str, Any]]:
    # 1. Chroma 검색
    raw_chroma = chroma_query(query_text, top_k=chroma_top_n)
    chroma_docs_raw: List[Dict[str, Any]] = []
    
    ids_list = raw_chroma.get("ids", [[]])[0] if raw_chroma.get("ids") else []
    docs_list = raw_chroma.get("documents", [[]])[0] if raw_chroma.get("documents") else []
    metas_list = raw_chroma.get("metadatas", [[]])[0] if raw_chroma.get("metadatas") else []
    dists_list = raw_chroma.get("distances", [[]])[0] if raw_chroma.get("distances") else []

    for _id, doc, meta, dist in zip(ids_list, docs_list, metas_list, dists_list):
        chroma_docs_raw.append({
            "id": _id, "text": doc, "metadata": meta or {}, "distance": float(dist),
        })

    chroma_ranked = _build_ranked_list_for_system("chroma", chroma_docs_raw, is_distance_score=True)

    # 2. BM25 검색
    bm25_raw = bm25_search(query_text, top_k=bm25_top_n)
    bm25_ranked = _build_ranked_list_for_system("bm25", bm25_raw, is_distance_score=False)

    # 3. RRF 결합
    ranked_lists = {"chroma": chroma_ranked, "bm25": bm25_ranked}
    fused = _rrf_fusion(ranked_lists, top_k=k, k=60)

    final_docs: List[Dict[str, Any]] = []
    for doc, rrf_score in fused:
        final_docs.append({
            "id": doc.doc_id,
            "text": doc.text,
            "metadata": doc.metadata,
            "rrf_score": rrf_score,
            "combined_score": doc.combined_score,
            "recency_score": doc.recency_score,
        })

    return final_docs