# saint/run_all.py
from pathlib import Path

from .common import Logger, normalize_token
from .major import crawl_major
from .gyopil import crawl_gyopil
from .gyosun import crawl_gyosun
from .chapel import crawl_chapel
from .gyojik import crawl_gyojik
from .cyber import crawl_cyber


YEARS = [
    "2020학년도",
    "2021학년도",
    "2022학년도",
    "2023학년도",
    "2024학년도",
    "2025학년도",
]

SEMS = [
    "1학기",
    "여름학기",
    "2학기",
    "겨울학기",
]


def run_all():
    base_dir = Path(__file__).resolve().parent  # saint 폴더
    data_root = base_dir / "data"

    for year in YEARS:
        for sem in SEMS:
            ytok = normalize_token(year)  # 예: "2020학년도" -> "2020"
            stok = normalize_token(sem)   # 예: "1학기" -> "1"

            combo_dir = data_root / f"{ytok}_{stok}"

            # 이 연도/학기에서 기대하는 결과 파일들
            expected_files = [
                combo_dir / f"saint_major_{ytok}_{stok}.jsonl",
                combo_dir / f"saint_gyopil_{ytok}_{stok}.jsonl",
                combo_dir / f"saint_gyosun_{ytok}_{stok}.jsonl",
                combo_dir / f"saint_chapel_{ytok}_{stok}.jsonl",
                combo_dir / f"saint_kyojik_{ytok}_{stok}.jsonl",
                combo_dir / f"saint_cyber_{ytok}_{stok}.jsonl",
            ]

            # ✅ 이미 모든 jsonl 이 있으면 이 연도/학기는 통으로 스킵
            if combo_dir.exists() and all(p.exists() for p in expected_files):
                print(f"[SKIP] {year} {sem} : 결과 파일이 이미 모두 존재해서 건너뜀")
                continue

            # 필요하면 폴더 생성
            combo_dir.mkdir(parents=True, exist_ok=True)

            log_path = combo_dir / "crawl_log.txt"
            logger = Logger(log_path)

            logger.log("=" * 80)
            logger.log(f"### {year} {sem} 크롤링 시작 ###")
            logger.log("=" * 80)

            try:
                crawl_major(year, sem, combo_dir, logger)
                crawl_gyopil(year, sem, combo_dir, logger)
                crawl_gyosun(year, sem, combo_dir, logger)
                crawl_chapel(year, sem, combo_dir, logger)
                crawl_gyojik(year, sem, combo_dir, logger)
                crawl_cyber(year, sem, combo_dir, logger)
            finally:
                logger.log(f"### {year} {sem} 크롤링 종료 ###")
                logger.flush()  # txt로 저장


if __name__ == "__main__":
    run_all()
