import sys
import logging
import threading
from typing import Dict, Any, List

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import BASE_DIR, RAG_PORT
from .indexing import reindex_all, update_incremental
from .query import rag_search
from .llm import generate_answer

# ---------------------------------------------------------
# 로그 설정
# ---------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
)

# ---------------------------------------------------------
# script/main.py (크롤러) import 준비
# ---------------------------------------------------------
SCRIPT_DIR = BASE_DIR / "script"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

try:
    # script/main.py 에 있는 main() 함수라고 가정
    from main import main as crawl_main
except ImportError as e:
    logger.error("Failed to import crawler main() from script/main.py: %s", e)
    crawl_main = None  # startup / endpoint 쪽에서 체크

# ---------------------------------------------------------
# 백그라운드 크롤링 상태 관리용 전역 변수
# ---------------------------------------------------------
crawl_state_lock = threading.Lock()
running_crawl: bool = False  # 현재 크롤링+인덱싱 스레드가 도는 중인지 여부

# ---------------------------------------------------------
# Pydantic 모델 정의
# ---------------------------------------------------------
class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 7


class RagDoc(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any]
    rrf_score: float | None = None
    combined_score: float | None = None
    recency_score: float | None = None


class CrawlAndIndexResponse(BaseModel):
    status: str
    indexed_documents: int


class CrawlKickResponse(BaseModel):
    status: str  # "started" | "already_running" | "error" 같은 값들

# 1. 응답 모델 수정
class RagQueryResponse(BaseModel):
    query: str
    answer: str          # <--- 추가: Gemini의 답변
    docs: List[RagDoc]   # 근거 문서들도 같이 리턴 (디버깅용)

# ---------------------------------------------------------
# FastAPI 앱
# ---------------------------------------------------------
app = FastAPI(title="GradChecker RAG API")


# ---------------------------------------------------------
# 공용: 크롤링 + 전체 인덱싱 수행 함수
# ---------------------------------------------------------
def run_crawl_and_index() -> int:
    """
    [수정됨] 스마트 업데이트 로직
    1. 크롤러 실행 (새 데이터 리스트 받음)
    2. 새 데이터가 있으면 -> update_incremental (부분 임베딩)
    3. 새 데이터가 없으면 -> 0 반환
    """
    if crawl_main is None:
        raise RuntimeError("Crawler main() error.")

    logger.info("[CRAWL] Starting crawler...")
    
    # 1. 크롤러 실행하고 '새 데이터' 받아오기
    # script/main.py 가 return all_new_data_list 하도록 수정되어 있어야 함
    new_data = crawl_main() 
    
    if not new_data:
        logger.info("[CRAWL] No new data found. Skipping index update.")
        return 0

    logger.info(f"[INDEX] Found {len(new_data)} new docs. Running incremental update...")
    
    # 2. 새로운 것만 임베딩 + BM25 갱신
    indexed_count = update_incremental(new_data)
    
    logger.info("[INDEX] Incremental update finished. Added docs=%s", indexed_count)
    return indexed_count


def run_crawl_and_index_background() -> None:
    """
    백그라운드에서 크롤링 + 인덱싱을 돌리는 래퍼.
    예외는 그냥 로그만 남기고 끝낸다.
    끝나면 running_crawl 플래그를 False 로 되돌린다.
    """
    global running_crawl

    try:
        logger.info("[BG-CRAWL] Background crawl+index started...")
        run_crawl_and_index()
        logger.info("[BG-CRAWL] Background crawl+index finished.")
    except Exception as e:
        logger.exception("[BG-CRAWL] Background crawl+index failed: %s", e)
    finally:
        # 어떤 경우에도 플래그를 내려줘야 다음 요청에서 다시 실행 가능
        with crawl_state_lock:
            running_crawl = False
            logger.info("[BG-CRAWL] running_crawl flag cleared.")


# ---------------------------------------------------------
# 서버 시작 시 1회 자동 크롤링 + 인덱싱
# ---------------------------------------------------------
@app.on_event("startup")
async def startup_event() -> None:
    """
    서버 프로세스가 시작될 때 한 번 실행.
    - 최신 공지 크롤링
    - Chroma + BM25 전체 인덱싱
    """
    try:
        logger.info("[STARTUP] Initial crawl + index started...")
        run_crawl_and_index()
        logger.info("[STARTUP] Initial crawl + index completed.")
    except Exception as e:
        # 여기서 예외를 터뜨리면 서버가 아예 안 뜰 수 있으니,
        # 로그만 남기고 서버는 일단 뜨도록 처리.
        logger.exception("[STARTUP] Initial crawl/index failed: %s", e)


# ---------------------------------------------------------
# 헬스체크
# ---------------------------------------------------------
@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


# ---------------------------------------------------------
# 수동 크롤링 + 인덱싱 (백엔드에서 1시간마다 호출)
# ---------------------------------------------------------
@app.post("/internal/crawl-and-index", response_model=CrawlKickResponse)
async def crawl_and_index_endpoint() -> CrawlKickResponse:
    """
    백엔드(Spring)에서 1시간마다 호출.
    - 크롤링 + 인덱싱은 백그라운드 스레드에서 실행
    - 이 엔드포인트는 바로 응답을 돌려준다.
    - 이미 백그라운드 작업이 돌고 있으면 새로 시작하지 않는다.
    """
    global running_crawl

    with crawl_state_lock:
        if running_crawl:
            logger.info("[CRAWL+INDEX] Request ignored: already running in background.")
            return CrawlKickResponse(status="already_running")

        # 아직 안 돌고 있으면 플래그 올리고 스레드 시작
        running_crawl = True
        logger.info("[CRAWL+INDEX] Kicking off new background crawl+index thread.")

    thread = threading.Thread(
        target=run_crawl_and_index_background,
        daemon=True,
    )
    thread.start()

    return CrawlKickResponse(status="started")


# ---------------------------------------------------------
# RAG 검색 엔드포인트
# ---------------------------------------------------------
@app.post("/rag/query", response_model=RagQueryResponse)
async def rag_query_endpoint(payload: RagQueryRequest) -> RagQueryResponse:
    try:
        # 1. 검색 (Retrieval)
        docs = rag_search(payload.query, top_k=payload.top_k)
        
        # 2. 생성 (Generation)
        # 검색된 문서가 없으면 바로 답변 처리
        if not docs:
            answer = "죄송합니다. 관련 정보를 찾을 수 없습니다."
        else:
            answer = generate_answer(payload.query, docs)

        return RagQueryResponse(
            query=payload.query, 
            answer=answer, 
            docs=docs
        )
    except Exception as e:
        logger.exception("RAG search failed: %s", e)
        raise HTTPException(status_code=500, detail=f"RAG search failed: {e}")
    
# ---------------------------------------------------------
# uvicorn 실행 함수
# ---------------------------------------------------------
def start() -> None:
    """
    python -m rag.server 로 실행할 때 사용하는 진입점.
    """
    uvicorn.run(
        "rag.server:app",
        host="0.0.0.0",
        port=RAG_PORT,
        reload=False,
    )


if __name__ == "__main__":
    start()
