import os
import time
import json

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)


# ===== 공통 대기 함수 =====
def short_pause(seconds: float = 0.5):
    time.sleep(seconds)


# ===== 콤보박스 옵션 텍스트 모두 가져오기 (열고 -> 읽고 -> 닫기) =====
def get_combo_texts(driver, wait: WebDriverWait, box_id: str, scroll_id: str):
    """
    box_id   : 콤보 입력 박스 ID (예: WDFA, WD010A, WD010D)
    scroll_id: 드롭다운 리스트 영역 ID (예: WDFB-scrl, WD010B-scrl, WD010E-scrl)

    콤보를 열고(scroll_id 안의 전체 div에서 줄 단위로 텍스트를 읽은 뒤),
    콤보를 다시 닫고 리스트를 반환한다.
    """
    # 1) 콤보 열기
    box = wait.until(EC.element_to_be_clickable((By.ID, box_id)))
    box.click()
    short_pause()

    # 2) 리스트 안의 모든 div (descendant) 수집
    elems = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, f"//div[@id='{scroll_id}']//div")
        )
    )

    names = []
    seen = set()

    for el in elems:
        text = el.text or ""
        for line in text.splitlines():
            txt = line.strip()
            if not txt:
                continue
            if "선택" in txt or txt in ("전체",):
                continue
            if txt in seen:
                continue
            seen.add(txt)
            names.append(txt)

    # 3) 콤보 닫기 (바디 아무 데나 클릭)
    try:
        driver.find_element(By.TAG_NAME, "body").click()
        short_pause()
        # 리스트가 사라졌는지 한 번 더 확인
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, scroll_id))
            )
        except TimeoutException:
            # 안 사라졌어도 크게 문제는 없으니 패스
            pass
    except Exception:
        pass

    return names


# ===== 결과 테이블 파싱 함수 =====
def parse_result_table(driver, wait, year_text: str, sem_text: str, major_name: str):
    """
    현재 iframe(수강신청/교과과정 화면)에서 결과 테이블을 찾아
    학년도/학기/학과명 컬럼을 앞에 붙인 dict 리스트를 반환.
    - WebDynpro 테이블: tbody[id$='contentTBody'] 안의
      rt='2' 헤더행, rt='1' 데이터행 구조를 이용.
    """
    rows_data = []

    try:
        tbodies = driver.find_elements(
            By.XPATH, "//tbody[starts-with(@id,'WD') and contains(@id,'contentTBody')]"
        )
    except Exception:
        print(f"[WARN] '{major_name}' : tbody 후보를 찾지 못했음")
        return rows_data

    target_tbody = None
    headers = []

    for tb in tbodies:
        try:
            header_tr = tb.find_element(By.XPATH, "./tr[@rt='2']")
            header_ths = header_tr.find_elements(By.XPATH, "./th")
            headers_text = [" ".join(th.text.split()) for th in header_ths]

            if "과목번호" in headers_text and "수강인원" in headers_text:
                target_tbody = tb
                headers = headers_text
                break

        except (NoSuchElementException, StaleElementReferenceException):
            continue

    if target_tbody is None:
        print(f"[WARN] '{major_name}' : 결과 테이블을 찾지 못했음")
        return rows_data

    print(f"   - 헤더: {headers}")

    data_trs = target_tbody.find_elements(By.XPATH, "./tr[@rt='1']")

    for tr in data_trs:
        try:
            tds = tr.find_elements(By.XPATH, "./td")
        except StaleElementReferenceException:
            continue

        if len(tds) != len(headers):
            continue

        values = [" ".join(td.text.split()) for td in tds]

        row = {
            "학년도": year_text,
            "학기": sem_text,
            "학과명": major_name,
        }
        for h, v in zip(headers, values):
            row[h] = v

        rows_data.append(row)

    return rows_data


# ===== 학년도 / 학기 설정 함수 =====
def set_year_and_semester(wait, year_label: str, sem_label: str):
    """
    상단의 학년도(WD89), 학기(WDDD) 콤보박스를
    year_label / sem_label 로 변경한다.
    예) year_label='2024학년도', sem_label='1학기'
    """
    year_input = wait.until(EC.element_to_be_clickable((By.ID, "WD89")))
    year_input.click()
    short_pause()

    year_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[normalize-space()='{year_label}']")
        )
    )
    year_option.click()
    short_pause()

    sem_input = wait.until(EC.element_to_be_clickable((By.ID, "WDDD")))
    sem_input.click()
    short_pause()

    sem_option = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[normalize-space()='{sem_label}']")
        )
    )
    sem_option.click()
    short_pause()


def main():
    load_dotenv()
    SSU_ID = os.getenv("SSU_ID")
    SSU_PW = os.getenv("SSU_PW")

    if not SSU_ID or not SSU_PW:
        raise RuntimeError("SSU_ID / SSU_PW 를 .env 에 설정해 주세요.")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=2560,1400")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        # 1) u-SAINT 포털 접속
        driver.get("https://saint.ssu.ac.kr/irj/portal")
        short_pause()

        # 2) 메인 화면 "로그인" 버튼 클릭
        login_btn = wait.until(EC.element_to_be_clickable((By.ID, "s_btnLogin")))
        login_btn.click()
        short_pause()

        # 3) smartid 로그인 페이지 대기
        wait.until(EC.url_contains("smartid.ssu.ac.kr/Symtra_sso"))
        short_pause()

        # 4) 아이디 / 비밀번호 입력
        id_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        pw_input = wait.until(EC.presence_of_element_located((By.ID, "pwd")))

        id_input.clear()
        id_input.send_keys(SSU_ID)
        short_pause()

        pw_input.clear()
        pw_input.send_keys(SSU_PW)
        short_pause()

        # 5) 로그인 버튼 클릭
        sso_login_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_login, button.btn_login"))
        )
        sso_login_btn.click()
        short_pause()

        # 6) 다시 포털 메인으로 돌아올 때까지 대기
        wait.until(EC.url_contains("saint.ssu.ac.kr/irj/portal"))
        short_pause()

        # 7) 상단 메뉴에서 "학사관리" 클릭
        haksa_menu = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class,'depth1') and normalize-space()='학사관리']",
                )
            )
        )
        haksa_menu.click()
        short_pause()

        # 8) "수강신청/교과과정" 클릭
        course_menu = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//a[contains(@class,'c_nodeA') and normalize-space()='수강신청/교과과정']",
                )
            )
        )
        course_menu.click()
        short_pause()

        # ===== 수강신청/교과과정 화면 로딩 =====
        time.sleep(3)  # iframe 두 겹 진입 전 3초 대기

        # 9) 바깥 iframe(contentAreaFrame) 으로 진입
        wait.until(EC.presence_of_element_located((By.ID, "contentAreaFrame")))
        driver.switch_to.frame("contentAreaFrame")
        short_pause()

        # 10) 안쪽 iframe(isolatedWorkArea) 으로 진입
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "isolatedWorkArea")))
        short_pause()

        # 11) 학부전공별 탭이 아니면 한번 눌러주기
        try:
            tab_hakbu = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@role='tab' and normalize-space()='학부전공별']")
                )
            )
            tab_hakbu.click()
            short_pause()
        except Exception:
            pass

        # ==== 학년도 / 학기: 2024학년도 1학기 고정 ====
        set_year_and_semester(wait, "2024학년도", "1학기")

        cur_year = wait.until(
            EC.presence_of_element_located((By.ID, "WD89"))
        ).get_attribute("value")
        cur_sem = wait.until(
            EC.presence_of_element_located((By.ID, "WDDD"))
        ).get_attribute("value")
        print(f"[INFO] 현재 학년도/학기: {cur_year}, {cur_sem}")

        # ==== 대학 콤보의 전체 항목 읽기 ====
        college_names = get_combo_texts(driver, wait, "WDFA", "WDFB-scrl")
        print(f"[INFO] 대학 목록: {college_names}")

        all_rows = []

        # ===== 대학 루프 =====
        for c_idx, college in enumerate(college_names, start=1):
            print(f"\n==== 대학 ({c_idx}/{len(college_names)}): {college} ====")

            # 대학 선택 (항상 닫힌 상태에서 다시 열어서 선택)
            college_box = wait.until(EC.element_to_be_clickable((By.ID, "WDFA")))
            college_box.click()
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
                print(f"[WARN] 대학 '{college}' 선택 실패, 건너뜀")
                # 혹시 열려 있으면 닫기
                driver.find_element(By.TAG_NAME, "body").click()
                short_pause()
                continue

            # 학부 목록 읽기
            try:
                dept_names = get_combo_texts(driver, wait, "WD010A", "WD010B-scrl")
            except TimeoutException:
                print(f"[WARN] 대학 '{college}' : 학부 콤보 없음, 건너뜀")
                continue

            print(f"   [INFO] 학부 목록: {dept_names}")

            # ===== 학부 루프 =====
            for d_idx, dept in enumerate(dept_names, start=1):
                print(f"\n   == 학부 ({d_idx}/{len(dept_names)}): {dept} ==")

                dept_box = wait.until(EC.element_to_be_clickable((By.ID, "WD010A")))
                dept_box.click()
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
                    print(f"   [WARN] 학부 '{dept}' 선택 실패, 건너뜀")
                    driver.find_element(By.TAG_NAME, "body").click()
                    short_pause()
                    continue

                # 전공 목록 읽기
                try:
                    major_names = get_combo_texts(driver, wait, "WD010D", "WD010E-scrl")
                except TimeoutException:
                    print(f"   [WARN] 학부 '{dept}' : 전공 콤보 없음, 건너뜀")
                    continue

                print(f"      [INFO] 전공 목록: {major_names}")

                # ===== 전공 루프 =====
                for m_idx, major in enumerate(major_names, start=1):
                    print(
                        f"      -- 전공 ({m_idx}/{len(major_names)}): "
                        f"{college} / {dept} / {major}"
                    )

                    major_box = wait.until(EC.element_to_be_clickable((By.ID, "WD010D")))
                    major_box.click()
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
                        print(f"      [WARN] 전공 '{major}' 선택 실패, 건너뜀")
                        driver.find_element(By.TAG_NAME, "body").click()
                        short_pause()
                        continue

                    # 검색 버튼
                    for attempt in range(2):
                        try:
                            search_btn = wait.until(
                                EC.element_to_be_clickable((By.ID, "WD0110"))
                            )
                            search_btn.click()
                            short_pause()
                            break
                        except StaleElementReferenceException:
                            print("         - 검색 버튼 stale, 다시 찾는 중...")
                            short_pause(1.0)
                    else:
                        print("         - 검색 버튼 클릭 실패, 이 전공은 건너뜀")
                        continue

                    print("         - 검색 후 10초 대기 중...")
                    time.sleep(10)

                    # 검색 결과 테이블 파싱
                    rows = parse_result_table(driver, wait, cur_year, cur_sem, major)
                    print(f"         - {len(rows)}개 행 수집")
                    all_rows.extend(rows)

        # ==== JSONL로 저장 ====
        out_path = "saint_courses.jsonl"
        with open(out_path, "w", encoding="utf-8") as f:
            for row in all_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        print(f"\n[DONE] 총 {len(all_rows)}개 행을 {out_path} 에 저장했습니다.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
