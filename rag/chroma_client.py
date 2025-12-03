# rag/chroma_client.py
from __future__ import annotations
from typing import List, Dict, Any

import chromadb
from chromadb.api.models.Collection import Collection

from .config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from .embeddings import embed_texts

_client: chromadb.PersistentClient | None = None
_collection: Collection | None = None


def get_client() -> chromadb.PersistentClient:
    """
    Chroma PersistentClient 싱글톤 생성.
    """
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
    return _client


def get_collection() -> Collection:
    """
    ss u_notices 컬렉션 가져오기 (없으면 생성).
    """
    global _collection
    if _collection is None:
        client = get_client()
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            # 필요한 경우 metadata config 추가 가능
        )
    return _collection


def add_documents(
    ids: List[str],
    texts: List[str],
    metadatas: List[Dict[str, Any]],
) -> None:
    """
    새 문서들을 임베딩해서 Chroma 컬렉션에 추가 (upsert 방식).
    - ids: 각 문서의 고유 ID (우리는 link를 쓸 예정)
    - texts: 실제 검색에 사용할 텍스트 (title + content)
    - metadatas: 부가 정보 (dept, date, url 등)
    """
    if not ids:
        return

    if not (len(ids) == len(texts) == len(metadatas)):
        raise ValueError("ids, texts, metadatas 길이가 다릅니다.")

    embeddings = embed_texts(texts)
    collection = get_collection()

    # 이미 존재하는 id면 덮어쓰고, 없으면 새로 추가
    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def query(
    query_text: str,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    쿼리 텍스트 하나로 유사 문서 top_k개를 검색.
    반환값 예시:
    {
      "ids": [[...]],
      "distances": [[...]],
      "documents": [[...]],
      "metadatas": [[...]],
    }
    """
    query_vec = embed_texts([query_text])[0]
    collection = get_collection()

    result = collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["metadatas", "documents", "distances"],
    )
    return result
