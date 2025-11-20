# saint/major.py
import time
import json
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException,  # ⬅ 추가
)

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
)


def safe_click(
    driver,
    wait: WebDriverWait,
    logger: Logger,
    locator,
    desc: str,
    max_retry: int = 3,
):
    """
    ur-loading-box 로딩 레이어/DOM 변경 때문에 click 이 가로막힐 때를
    대비한 안전 클릭 헬퍼.
    """
    for attempt in range(1, max_retry + 1):
        try:
            el = wait.until(EC.element_to_be_clickable(locator))
            # 화면 중앙으로 스크롤
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
            time.sleep(0.2)
            el.click()
            return el
        except ElementClickInterceptedException:
            logger.log(
                f"[WARN]{desc} 클릭 시 로딩 레이어에 가로막힘 "
                f"({attempt}/{max_retry}회 재시도)..."
            )
        except StaleElementReferenceException:
            logger.log(
                f"[WARN]{desc} 클릭 대상이 stale 상태 "
                f"({attempt}/{max_retry}회 재시도)..."
            )
        except TimeoutException:
            logger.log(
                f"[WARN]{desc} element_to_be_clickable 대기 Timeout "
                f"({attempt}/{max_retry}회 재시도)..."
            )

        # 로딩 오버레이가 있으면 사라질 때까지 한번 기다려 봄
        try:
            wait.until(
                EC.invisibility_of_element_located((By.ID, "ur-loading-box"))
            )
        except TimeoutException:
            # 계속 떠 있어도 어차피 다음 루프에서 다시 시도
            pass
        time.sleep(0.5)

    raise TimeoutException(f"{desc} 클릭 실패 (재시도 {max_retry}회 초과)")


def crawl_major(year_label: str, sem_label: str, out_dir: Path, logger: Logger):
    """
    학부전공별 탭 크롤링.
    - 결과 JSONL: saint_major_년도_학기.jsonl  (테이블 컬럼만 그대로)
    """
    driver = create_driver()
    wait = WebDriverWait(driver, 30)

    year_token = normalize_token(year_label)
    sem_token = normalize_token(sem_label)
    out_path = out_dir / f"saint_major_{year_token}_{sem_token}.jsonl"

    all_rows: list[dict] = []

    try:
        # 공통: 로그인 + iframe 진입
        login_and_open_workarea(driver, wait, logger)
        switch_tab(wait, "학부전공별")

        # 학년도/학기 설정
        set_year_and_semester(wait, year_label, sem_label)

        cur_year = wait.until(
            EC.presence_of_element_located((By.ID, "WD89"))
        ).get_attribute("value")
        cur_sem = wait.until(
            EC.presence_of_element_located((By.ID, "WDDD"))
        ).get_attribute("value")
        logger.log(f"[INFO][학부전공별] 현재 학년도/학기: {cur_year}, {cur_sem}")

        # 대학 목록
        college_names = get_combo_texts(
            driver, wait, "WDFA", "WDFB-scrl", logger
        )
        logger.log(f"[INFO][학부전공별] 대학 목록: {college_names}")

        # ===== 대학 루프 =====
        for c_idx, college in enumerate(college_names, start=1):
            logger.log(
                f"\n==== [학부전공별] 대학 ({c_idx}/{len(college_names)}): {college} ===="
            )

            # 대학 콤보 열기 + 선택 (안전 클릭)
            college_box = safe_click(
                driver,
                wait,
                logger,
                (By.ID, "WDFA"),
                "[학부전공별] 대학 콤보",
            )
            short_pause()

            try:
                college_option = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            f"//div[@id='WDFB-scrl']//div[normalize-space()='{college}']",
                        )
                    )
                )
                college_option.click()
                short_pause()
            except TimeoutException:
                logger.log(f"[WARN] 대학 '{college}' 선택 실패, 건너뜀")
                driver.find_element(By.TAG_NAME, "body").click()
                short_pause()
                continue

            # 학부 목록
            try:
                dept_names = get_combo_texts(
                    driver, wait, "WD010A", "WD010B-scrl", logger
                )
            except TimeoutException:
                logger.log(f"[WARN] 대학 '{college}' : 학부 콤보 없음, 건너뜀")
                continue

            logger.log(f"   [INFO] 학부 목록: {dept_names}")

            # ===== 학부 루프 =====
            for d_idx, dept in enumerate(dept_names, start=1):
                logger.log(
                    f"\n   == 학부 ({d_idx}/{len(dept_names)}): {dept} =="
                )

                # 학부 콤보 열기 (안전 클릭)
                dept_box = safe_click(
                    driver,
                    wait,
                    logger,
                    (By.ID, "WD010A"),
                    "[학부전공별] 학부 콤보",
                )
                short_pause()

                try:
                    dept_option = wait.until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                f"//div[@id='WD010B-scrl']//div[normalize-space()='{dept}']",
                            )
                        )
                    )
                    dept_option.click()
                    short_pause()
                except TimeoutException:
                    logger.log(f"   [WARN] 학부 '{dept}' 선택 실패, 건너뜀")
                    driver.find_element(By.TAG_NAME, "body").click()
                    short_pause()
                    continue

                # 전공 목록
                try:
                    major_names = get_combo_texts(
                        driver, wait, "WD010D", "WD010E-scrl", logger
                    )
                except TimeoutException:
                    logger.log(
                        f"   [WARN] 학부 '{dept}' : 전공 콤보 없음, 건너뜀"
                    )
                    continue

                logger.log(f"      [INFO] 전공 목록: {major_names}")

                # ===== 전공 루프 =====
                for m_idx, major in enumerate(major_names, start=1):
                    logger.log(
                        f"      -- 전공 ({m_idx}/{len(major_names)}): "
                        f"{college} / {dept} / {major}"
                    )

                    # 전공 콤보 열기 (안전 클릭)
                    major_box = safe_click(
                        driver,
                        wait,
                        logger,
                        (By.ID, "WD010D"),
                        "[학부전공별] 전공 콤보",
                    )
                    short_pause()

                    try:
                        major_option = wait.until(
                            EC.element_to_be_clickable(
                                (
                                    By.XPATH,
                                    f"//div[@id='WD010E-scrl']//div[normalize-space()='{major}']",
                                )
                            )
                        )
                        major_option.click()
                        short_pause()
                    except TimeoutException:
                        logger.log(
                            f"      [WARN] 전공 '{major}' 선택 실패, 건너뜀"
                        )
                        driver.find_element(By.TAG_NAME, "body").click()
                        short_pause()
                        continue

                    # 검색 버튼 (안전 클릭)
                    try:
                        safe_click(
                            driver,
                            wait,
                            logger,
                            (By.ID, "WD0110"),
                            "[학부전공별] 검색 버튼",
                            max_retry=3,
                        )
                    except TimeoutException:
                        logger.log(
                            "         - 검색 버튼 클릭 실패, 이 전공은 건너뜀"
                        )
                        continue

                    logger.log("         - 검색 후 10초 대기 중...")
                    time.sleep(10)

                    # 결과 테이블 파싱 (학년도/학기/학과명 컬럼은 붙이지 않음)
                    rows = parse_table_generic(
                        driver,
                        wait,
                        logger,
                        table_name_for_log=major,
                        extra_columns=None,
                    )
                    logger.log(f"         - {len(rows)}개 행 수집")
                    all_rows.extend(rows)

        # ==== JSONL 저장 ====
        out_dir.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        logger.log(
            f"\n[DONE][학부전공별] 총 {len(all_rows)}개 행을 {out_path} 에 저장했습니다."
        )

    finally:
        driver.quit()
