# saint/common.py
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


# ===== 간단 대기 =====
def short_pause(seconds: float = 0.5):
    time.sleep(seconds)


# ===== 로그 유틸 =====
class Logger:
    def __init__(self, log_path: Path | None = None):
        self.log_path = Path(log_path) if log_path else None
        self.lines: list[str] = []

    def log(self, msg: str = ""):
        print(msg)
        self.lines.append(msg)

    def flush(self):
        if not self.log_path:
            return
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("w", encoding="utf-8") as f:
            f.write("\n".join(self.lines))


# ===== XPath용 문자열 리터럴 안전하게 만들기 (교양선택 계열에서 사용) =====
def build_xpath_text_literal(text: str) -> str:
    """
    XPath에서 문자열 리터럴로 안전하게 쓸 수 있게 변환.
    - 작은따옴표만 없는 경우: '텍스트'
    - 큰따옴표만 없는 경우: "텍스트"
    - 둘 다 있는 경우: concat('조각1',"'",'조각2',...)
    """
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'

    parts = text.split("'")
    concat_parts = []
    for i, part in enumerate(parts):
        if part:
            concat_parts.append(f"'{part}'")
        if i != len(parts) - 1:
            concat_parts.append('"\'"')  # 실제 ' 문자
    return "concat(" + ", ".join(concat_parts) + ")"


# ===== 드라이버 공통 생성 =====
def create_driver() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=2560,1400")
    driver = webdriver.Chrome(options=options)
    return driver


# ===== 로그인 + iframe 진입 =====
def login_and_open_workarea(driver: webdriver.Chrome, wait: WebDriverWait, logger: Logger):
    load_dotenv()
    SSU_ID = os.getenv("SSU_ID")
    SSU_PW = os.getenv("SSU_PW")

    if not SSU_ID or not SSU_PW:
        raise RuntimeError("SSU_ID / SSU_PW 를 .env 에 설정해 주세요.")

    logger.log("[INFO] u-SAINT 접속 중...")
    driver.get("https://saint.ssu.ac.kr/irj/portal")
    short_pause()

    # 메인 화면 로그인 버튼
    login_btn = wait.until(EC.element_to_be_clickable((By.ID, "s_btnLogin")))
    login_btn.click()
    short_pause()

    # smartid 페이지
    wait.until(EC.url_contains("smartid.ssu.ac.kr/Symtra_sso"))
    short_pause()

    # 아이디 / 비번
    id_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
    pw_input = wait.until(EC.presence_of_element_located((By.ID, "pwd")))

    id_input.clear()
    id_input.send_keys(SSU_ID)
    short_pause()

    pw_input.clear()
    pw_input.send_keys(SSU_PW)
    short_pause()

    sso_login_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn_login, button.btn_login"))
    )
    sso_login_btn.click()
    short_pause()

    # 포털 메인 복귀
    wait.until(EC.url_contains("saint.ssu.ac.kr/irj/portal"))
    short_pause()

    # 학사관리 → 수강신청/교과과정
    haksa_menu = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'depth1') and normalize-space()='학사관리']")
        )
    )
    haksa_menu.click()
    short_pause()

    course_menu = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@class,'c_nodeA') and normalize-space()='수강신청/교과과정']")
        )
    )
    course_menu.click()
    short_pause()

    # iframe 두 겹 진입
    time.sleep(3)
    wait.until(EC.presence_of_element_located((By.ID, "contentAreaFrame")))
    driver.switch_to.frame("contentAreaFrame")
    short_pause()

    wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "isolatedWorkArea")))
    short_pause()


# ===== 학년도 / 학기 설정 =====
def set_year_and_semester(wait: WebDriverWait, year_label: str, sem_label: str):
    # 학년도
    year_input = wait.until(EC.element_to_be_clickable((By.ID, "WD89")))
    year_input.click()
    short_pause()

    year_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{year_label}']"))
    )
    year_option.click()
    short_pause()

    # 학기
    sem_input = wait.until(EC.element_to_be_clickable((By.ID, "WDDD")))
    sem_input.click()
    short_pause()

    sem_option = wait.until(
        EC.element_to_be_clickable((By.XPATH, f"//div[normalize-space()='{sem_label}']"))
    )
    sem_option.click()
    short_pause()


# ===== 탭 전환 =====
def switch_tab(wait: WebDriverWait, tab_name: str):
    tab = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//div[@role='tab' and normalize-space()='{tab_name}']")
        )
    )
    tab.click()
    short_pause()


# ===== 콤보박스 전체 옵션 읽기 (학부전공 / 교양 계열 공통) =====
def get_combo_texts(driver, wait: WebDriverWait, box_id: str, scroll_id: str, logger: Logger | None = None):
    box = wait.until(EC.element_to_be_clickable((By.ID, box_id)))
    box.click()
    short_pause()

    elems = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, f"//div[@id='{scroll_id}']//div"))
    )

    names: list[str] = []
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

    try:
        driver.find_element(By.TAG_NAME, "body").click()
        short_pause()
        try:
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, scroll_id))
            )
        except TimeoutException:
            pass
    except Exception:
        pass

    if logger:
        logger.log(f"[DEBUG] {box_id}/{scroll_id} 옵션 개수: {len(names)}")

    return names


# ===== 결과 테이블 파싱 (공통) =====
def parse_table_generic(
    driver,
    wait: WebDriverWait,
    logger: Logger,
    table_name_for_log: str,
    extra_columns: dict | None = None,
):
    """
    WebDynpro 그리드 테이블 공통 파서.
    - header rt='2', data rt='1'
    - extra_columns: {'학년도': ..., '학기': ..., '교양분류명': ...} 같은 prefix
    """
    rows_data: list[dict] = []

    try:
        tbodies = driver.find_elements(
            By.XPATH, "//tbody[starts-with(@id,'WD') and contains(@id,'contentTBody')]"
        )
    except Exception:
        logger.log(f"[WARN] '{table_name_for_log}' : tbody 후보를 찾지 못했음")
        return rows_data

    target_tbody = None
    headers: list[str] = []

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
        logger.log(f"[WARN] '{table_name_for_log}' : 결과 테이블을 찾지 못했음")
        return rows_data

    logger.log(f"   - 헤더: {headers}")

    data_trs = target_tbody.find_elements(By.XPATH, "./tr[@rt='1']")

    for idx, tr in enumerate(data_trs, start=1):
        # 각 행마다 최대 3번까지 재시도
        for attempt in range(3):
            try:
                tds = tr.find_elements(By.XPATH, "./td")
                if len(tds) != len(headers):
                    raise StaleElementReferenceException("cols mismatch / maybe re-rendered")

                # 여기서 stale 이 자주 터져서 try 안으로 넣음
                values = [" ".join(td.text.split()) for td in tds]

                row = dict(extra_columns) if extra_columns else {}
                for h, v in zip(headers, values):
                    row[h] = v

                rows_data.append(row)
                break  # 이 행 성공 → 다음 행으로
            except StaleElementReferenceException:
                if attempt == 2:
                    logger.log(
                        f"   [WARN] '{table_name_for_log}' 행 {idx} 가 stale 상태라 건너뜀"
                    )
                    break
                # 잠깐 쉬고 다시 시도
                short_pause(0.3)
                continue

    return rows_data


# ===== 토큰 변환 (폴더명/파일명용) =====
def normalize_token(label: str) -> str:
    digits = "".join(ch for ch in label if ch.isdigit())
    return digits or label
