# saint/chapel.py
import time
import json
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from .common import (
    short_pause,
    create_driver,
    login_and_open_workarea,
    switch_tab,
    set_year_and_semester,
    get_combo_texts,
    parse_table_generic,
    Logger,
    normalize_token,
    build_xpath_text_literal,
)


def crawl_chapel(year_label: str, sem_label: str, out_dir: Path, logger: Logger):
    """
    채플 탭 크롤링.
    - 드롭다운( WD01E1-btn / WD01E2-scrl ) 순회
    - 검색 버튼: WD01E6
    - saint_chapel_년도_학기.jsonl
      컬럼: 학년도, 학기, 채플분류명 + 테이블 헤더
    """
    driver = create_driver()
    wait = WebDriverWait(driver, 30)

    year_token = normalize_token(year_label)
    sem_token = normalize_token(sem_label)
    out_path = out_dir / f"saint_chapel_{year_token}_{sem_token}.jsonl"

    all_rows: list[dict] = []

    try:
        login_and_open_workarea(driver, wait, logger)
        switch_tab(wait, "채플")

        set_year_and_semester(wait, year_label, sem_label)

        cur_year = wait.until(
            EC.presence_of_element_located((By.ID, "WD89"))
        ).get_attribute("value")
        cur_sem = wait.until(
            EC.presence_of_element_located((By.ID, "WDDD"))
        ).get_attribute("value")
        logger.log(f"[INFO][채플] 현재 학년도/학기: {cur_year}, {cur_sem}")

        group_names = get_combo_texts(driver, wait, "WD01E1", "WD01E2-scrl", logger)
        logger.log(f"[INFO][채플] 분류 목록({len(group_names)}개): {group_names}")

        if not group_names:
            debug_path = out_dir / f"chapel_dropdown_debug_{year_token}_{sem_token}.html"
            debug_path.write_text(driver.page_source, encoding="utf-8")
            logger.log(f"[WARN] 채플 드롭다운 비어 있음. HTML을 {debug_path} 로 저장.")
            return

        for idx, name in enumerate(group_names, start=1):
            logger.log(f"\n==== [채플] ({idx}/{len(group_names)}) '{name}' 검색 ====")

            try:
                arrow = wait.until(EC.element_to_be_clickable((By.ID, "WD01E1-btn")))
                driver.execute_script("arguments[0].click();", arrow)
                short_pause()
            except TimeoutException:
                logger.log("   [WARN] 화살표 클릭 실패, 건너뜀")
                continue

            try:
                wait.until(EC.presence_of_element_located((By.ID, "WD01E2-scrl")))
            except TimeoutException:
                logger.log("   [WARN] WD01E2-scrl 안 뜸, 건너뜀")
                continue

            try:
                literal = build_xpath_text_literal(name)
                xpath = f"//div[@id='WD01E2-scrl']//div[normalize-space()={literal}]"
                option = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                driver.execute_script("arguments[0].click();", option)
                short_pause()
            except TimeoutException:
                logger.log(f"   [WARN] '{name}' 항목 선택 실패, 건너뜀")
                driver.find_element(By.TAG_NAME, "body").click()
                short_pause()
                continue

            # 검색 버튼: WD01E6
            for attempt in range(2):
                try:
                    search_btn = wait.until(EC.element_to_be_clickable((By.ID, "WD01E6")))
                    search_btn.click()
                    short_pause()
                    break
                except StaleElementReferenceException:
                    logger.log("   - 검색 버튼 stale, 다시 찾는 중...")
                    short_pause(1.0)
            else:
                logger.log("   - 검색 버튼 클릭 실패, 건너뜀")
                continue

            logger.log("   - 검색 후 10초 대기 중...")
            time.sleep(10)

            rows = parse_table_generic(
                driver,
                wait,
                logger,
                table_name_for_log=name,
                extra_columns={"학년도": cur_year, "학기": cur_sem, "채플분류명": name},
            )
            logger.log(f"   - {len(rows)}개 행 수집")
            all_rows.extend(rows)

        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.log(f"\n[DONE][채플] 총 {len(all_rows)}개 행을 {out_path} 에 저장했습니다.")

    finally:
        driver.quit()
