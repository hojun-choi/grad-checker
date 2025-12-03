# rag/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

# =========
# 프로젝트 루트 기준 경로 계산
# =========
BASE_DIR = Path(__file__).resolve().parent.parent  # .../grad-checker

# 루트에 있는 .env 로드
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

# =========
# 환경 변수들
# =========
RAG_PORT = int(os.getenv("RAG_PORT", "8000"))

# CHROMA_DB_DIR 이 상대 경로로 들어와도 루트 기준으로 바꿔줌
_chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
CHROMA_DB_DIR = str((BASE_DIR / _chroma_dir).resolve())

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")

# 나중에 쓸 수 있도록 CSV 경로도 미리 지정
_ssu_csv_default = "notices/ssu_notices.csv"
SSU_NOTICES_CSV_PATH = str((BASE_DIR / os.getenv("SSU_NOTICES_CSV_PATH", _ssu_csv_default)).resolve())

# Chroma 컬렉션 이름 (env에 없으면 기본값 사용)
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ssu_notices")
