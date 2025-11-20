# saint/gyojik.py
import time
import json
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .common import (
    create_driver,
    login_and_open_workarea,
    switch_tab,
    set_year_and_semester,
    parse_table_generic,
    Logger,
    normalize_token,
)


def crawl_gyojik(year_label: str, sem_label: str, out_dir: Path, logger: Logger):
    """
    교직 탭 크롤링.
    - 드롭다운 없이 검색 버튼만: WD01D5
    - saint_kyojik_년도_학기.jsonl
      컬럼: 학년도, 학기 + 테이블 헤더
    """
    driver = create_driver()
    wait = WebDriverWait(driver, 30)

    year_token = normalize_token(year_label)
    sem_token = normalize_token(sem_label)
    out_path = out_dir / f"saint_kyojik_{year_token}_{sem_token}.jsonl"

    all_rows: list[dict] = []

    try:
        login_and_open_workarea(driver, wait, logger)
        switch_tab(wait, "교직")

        set_year_and_semester(wait, year_label, sem_label)

        cur_year = wait.until(
            EC.presence_of_element_located((By.ID, "WD89"))
        ).get_attribute("value")
        cur_sem = wait.until(
            EC.presence_of_element_located((By.ID, "WDDD"))
        ).get_attribute("value")
        logger.log(f"[INFO][교직] 현재 학년도/학기: {cur_year}, {cur_sem}")

        # 검색 버튼 클릭: WD01D5
        search_btn = wait.until(EC.element_to_be_clickable((By.ID, "WD01D5")))
        search_btn.click()
        logger.log("[INFO][교직] 검색 버튼 클릭, 10초 대기 중...")
        time.sleep(10)

        rows = parse_table_generic(
            driver,
            wait,
            logger,
            table_name_for_log="교직",
            extra_columns={"학년도": cur_year, "학기": cur_sem},
        )
        logger.log(f"   - {len(rows)}개 행 수집")
        all_rows.extend(rows)

        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.log(f"\n[DONE][교직] 총 {len(all_rows)}개 행을 {out_path} 에 저장했습니다.")

    finally:
        driver.quit()
