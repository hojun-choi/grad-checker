import os
import time
import sys
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 모듈 임포트
from common import Logger, short_pause
from crawlers import major, gyopil, gyosun, chapel, kyojik, cyber

def main():
    load_dotenv()
    SSU_ID = os.getenv("SSU_ID")
    SSU_PW = os.getenv("SSU_PW")

    if not SSU_ID or not SSU_PW:
        raise RuntimeError("SSU_ID / SSU_PW 를 .env 에 설정해 주세요.")

    # 타겟 설정
    YEARS = [
        "2020학년도", "2021학년도", "2022학년도",
        "2023학년도", "2024학년도", "2025학년도"
    ]
    SEMESTERS = ["1학기", "여름학기", "2학기", "겨울학기"]
    
    # 브라우저 설정
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless") # 필요시 주석 해제
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)

    try:
        # 1. 로그인 및 접속
        print(">>> [LOGIN] u-SAINT 접속 중...")
        driver.get("https://saint.ssu.ac.kr/irj/portal")
        short_pause()

        wait.until(EC.element_to_be_clickable((By.ID, "s_btnLogin"))).click()
        short_pause()

        wait.until(EC.url_contains("smartid.ssu.ac.kr"))
        driver.find_element(By.ID, "userid").send_keys(SSU_ID)
        driver.find_element(By.ID, "pwd").send_keys(SSU_PW)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_login"))).click()
        short_pause()

        wait.until(EC.url_contains("saint.ssu.ac.kr/irj/portal"))
        print(">>> [LOGIN] 로그인 성공")

        # 2. 메뉴 진입
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'학사관리')]"))).click()
        short_pause()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'수강신청/교과과정')]"))).click()
        short_pause(3.0)

        # 3. iframe 진입 (한 번만 수행)
        wait.until(EC.presence_of_element_located((By.ID, "contentAreaFrame")))
        driver.switch_to.frame("contentAreaFrame")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "isolatedWorkArea")))
        print(">>> [IFRAME] 프레임 진입 완료")

        # 4. 루프 실행
        base_data_dir = os.path.join(os.getcwd(), "data")
        if not os.path.exists(base_data_dir):
            os.makedirs(base_data_dir)

        for year in YEARS:
            for sem in SEMESTERS:
                # 폴더 생성: data/2020학년도_1학기
                folder_name = f"{year}_{sem}"
                target_dir = os.path.join(base_data_dir, folder_name)
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                
                # 로그 파일 설정
                log_path = os.path.join(target_dir, "crawl_log.txt")
                logger = Logger(log_path)
                
                logger.log(f"==========================================")
                logger.log(f"   크롤링 시작: {year} {sem}")
                logger.log(f"   저장 경로: {target_dir}")
                logger.log(f"==========================================")

                # 순차적으로 크롤러 실행
                # 1) 학부전공별
                try:
                    major.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 학부전공별 중단: {e}")

                # 2) 교양필수
                try:
                    gyopil.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 교양필수 중단: {e}")

                # 3) 교양선택
                try:
                    gyosun.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 교양선택 중단: {e}")

                # 4) 채플
                try:
                    chapel.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 채플 중단: {e}")

                # 5) 교직
                try:
                    kyojik.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 교직 중단: {e}")

                # 6) 숭실사이버대
                try:
                    cyber.run(driver, wait, year, sem, target_dir, logger)
                except Exception as e:
                    logger.log(f"[CRITICAL ERROR] 숭실사이버대 중단: {e}")
                
                logger.log(f"\n>>> {year} {sem} 완료\n")
                
    except Exception as e:
        print(f"[FATAL] 메인 루프 에러: {e}")
    finally:
        time.sleep(2)
        driver.quit()
        print(">>> [EXIT] 드라이버 종료")

if __name__ == "__main__":
    main()