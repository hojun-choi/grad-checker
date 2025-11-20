# saint/cyber.py
import time
import json
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from .common import (
    create_driver,
    login_and_open_workarea,
    switch_tab,
    set_year_and_semester,
    parse_table_generic,
    Logger,
    normalize_token,
)


def crawl_cyber(year_label: str, sem_label: str, out_dir: Path, logger: Logger):
    """
    숭실사이버대 탭 크롤링.
    - 드롭다운 없이 검색 버튼만: WD01D5
    - saint_cyber_년도_학기.jsonl 로 저장
    """
    driver = create_driver()
    wait = WebDriverWait(driver, 30)

    year_token = normalize_token(year_label)
    sem_token = normalize_token(sem_label)
    out_path = out_dir / f"saint_cyber_{year_token}_{sem_token}.jsonl"

    all_rows: list[dict] = []

    try:
        login_and_open_workarea(driver, wait, logger)
        switch_tab(wait, "숭실사이버대")

        set_year_and_semester(wait, year_label, sem_label)

        cur_year = wait.until(
            EC.presence_of_element_located((By.ID, "WD89"))
        ).get_attribute("value")
        cur_sem = wait.until(
            EC.presence_of_element_located((By.ID, "WDDD"))
        ).get_attribute("value")
        logger.log(f"[INFO][사이버] 현재 학년도/학기: {cur_year}, {cur_sem}")

        # ✅ 검색 버튼: presence + JS 클릭 + 재시도
        clicked = False
        for attempt in range(1, 4):
            try:
                btn = wait.until(
                    EC.presence_of_element_located((By.ID, "WD01D5"))
                )
                # 혹시 화면 밖이면 스크롤
                driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", btn
                )
                time.sleep(0.3)
                # JS 로 강제 클릭
                driver.execute_script("arguments[0].click();", btn)

                logger.log(
                    f"[INFO][사이버] 검색 버튼 JS 클릭 성공 (시도 {attempt}/3), 10초 대기 중..."
                )
                time.sleep(10)
                clicked = True
                break
            except TimeoutException as e:
                logger.log(
                    f"[WARN][사이버] 검색 버튼 클릭 재시도 ({attempt}/3), 에러: {e.msg}"
                )
                time.sleep(1)

        if not clicked:
            debug_path = out_dir / f"cyber_debug_btn_{year_token}_{sem_token}.html"
            debug_path.write_text(driver.page_source, encoding="utf-8")
            logger.log(
                f"[ERROR][사이버] 검색 버튼을 끝내 찾지 못함. HTML을 {debug_path} 로 저장하고 종료합니다."
            )
            return

        # 결과 테이블 파싱
        rows = parse_table_generic(
            driver,
            wait,
            logger,
            table_name_for_log="사이버",
            extra_columns={"학년도": cur_year, "학기": cur_sem},
        )
        logger.log(f"   - {len(rows)}개 행 수집")
        all_rows.extend(rows)

        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.log(
            f"\n[DONE][사이버] 총 {len(all_rows)}개 행을 {out_path} 에 저장했습니다."
        )

    finally:
        driver.quit()
