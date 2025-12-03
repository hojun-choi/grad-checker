# rag/embeddings.py
from typing import List
import os
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
from FlagEmbedding import BGEM3FlagModel

from .config import EMBEDDING_MODEL_NAME

# 전역 싱글톤 모델 (lazy load)
_model: BGEM3FlagModel | None = None


def get_embedding_model() -> BGEM3FlagModel:
    """
    BGE-M3 임베딩 모델을 lazy 로드해서 재사용.
    """
    global _model
    if _model is None:
        # use_fp16=True: GPU 있으면 속도 향상, CPU여도 동작은 함
        _model = BGEM3FlagModel(
            EMBEDDING_MODEL_NAME,
            use_fp16=True,
        )
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    여러 개의 텍스트를 한 번에 임베딩해서 [ [float...], ... ] 형태로 반환.
    Chroma에 그대로 넣을 수 있는 포맷.
    """
    if not texts:
        return []

    model = get_embedding_model()

    outputs = model.encode(
        texts,
        batch_size=16,      # 나중에 GPU/CPU 상황 보고 조절
        max_length=8192,    # 필요 없으면 1024 ~ 2048 정도로 낮춰도 됨
        return_dense=True,
        return_sparse=False,
        return_colbert_vecs=False,
    )

    dense_vecs = outputs["dense_vecs"]  # shape: (N, 1024)
    # FlagEmbedding이 numpy.ndarray를 주니까, 그대로 리턴해도 되고
    # Chroma가 리스트도 받기 때문에 list로 변환해도 됨.
    return dense_vecs.tolist()
