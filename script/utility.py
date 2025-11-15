import time
import os
import pandas as pd # CSV 처리를 위해 pandas 사용
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# --- [ 1. 드라이버 및 수프 설정 (변경 없음) ] ---

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver 설정 완료")
        return driver
    except Exception as e:
        print(f"[드라이버 설정 에러] {e}")
        return None

def get_soup(driver, url, delay=0.5):
    driver.get(url)
    time.sleep(delay) 
    return BeautifulSoup(driver.page_source, "html.parser")

# --- [ 2. CSV 데이터 관리 함수 (JSON -> CSV로 변경) ] ---

def load_data(filename, id_columns=["title", "link"]): 
    """
    [CSV 버전] CSV 파일에서 기존 데이터를 로드합니다.
    (DataFrame과 기존 게시글 ID 세트를 반환)
    """
    if not os.path.exists(filename):
        print(f"기존 파일 '{filename}'이 없습니다. 새 수집을 시작합니다.")
        # 빈 DataFrame과 빈 세트 반환
        return pd.DataFrame(columns=id_columns), set()
        
    print(f"'{filename}' 파일을 찾았습니다. 기존 데이터를 로드합니다.")
    try:
        old_df = pd.read_csv(filename)
        
        # ID 세트 생성 (str로 통일)
        id_key1 = id_columns[0]
        id_key2 = id_columns[1]
        
        old_post_ids = set()
        if not old_df.empty:
             old_post_ids = set(zip(
                old_df[id_key1].astype(str), 
                old_df[id_key2].astype(str)
            ))
                
        print(f"총 {len(old_post_ids)}개의 기존 게시글 ID를 로드했습니다.")
        return old_df, old_post_ids 
        
    except pd.errors.EmptyDataError:
        print(f"'{filename}' 파일이 비어있습니다. 새 수집을 시작합니다.")
        return pd.DataFrame(columns=id_columns), set()
    except Exception as e:
        print(f"기존 CSV 파일 로드 중 오류: {e}. 새 파일로 시작합니다.")
        return pd.DataFrame(columns=id_columns), set() 

def save_data(df, filename): 
    """
    [CSV 버전] DataFrame을 CSV 파일로 저장합니다.
    (경로가 없으면 자동으로 생성)
    """
    try:
        # 파일이 저장될 디렉토리 경로를 확인하고, 없으면 생성
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # CSV로 저장 (encoding='utf-8-sig'는 Excel에서 한글 깨짐 방지)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\nCSV 저장 완료! '{filename}' (총 {len(df)}개)")
        
    except Exception as e:
        print(f"[에러] CSV 파일 저장 중 오류 발생: {e}")

def process_and_save_results(new_data_list, old_df, filename, id_columns=["title", "link"]): 
    """
    [CSV 버전] 새 데이터(list)와 기존 데이터(DataFrame)를 병합, 중복 제거 후 저장합니다.
    """
    if not new_data_list:
        print("병합할 새 데이터가 없습니다.")
        return 0

    new_df = pd.DataFrame(new_data_list)
    
    # 새 글(new_df)을 위로, 기존 글(old_df)을 아래로 합침
    combined_df = pd.concat([new_df, old_df], ignore_index=True)
    
    # 중복 제거 (새 데이터 우선)
    combined_df.drop_duplicates(subset=id_columns, keep="first", inplace=True)
    
    # CSV 저장 함수 호출
    save_data(combined_df, filename)
    
    return len(new_df)