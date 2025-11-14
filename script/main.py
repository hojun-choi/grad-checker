import os
from utility import *

# --- [ 크롤러 모듈 임포트 ] ---
try:
    
    #법과대학
    from law import globallaw
    from law import law
    #사회과학
    from social_science import socialwelfare
    from social_science import publicadministration
    from social_science import politicalscience_internationalrelations
    from social_science import informationsociology
    from social_science import journalism_publicrelation_advertising
    from social_science import lifelong_edu
    #경제통상대학
    from economy import economics
    from economy import global_commerce
    from economy import ecofinance
    from economy import internationaltrade_transaction
    #경영대학
    #require debugging. only crawls notice.
    #아니 이거 크롤링만 막아둔거 같은데? 왜않됢?
    from business import business_administration
    from business import venture_smallbusiness
    from business import accounting
    from business import finance
    from business import venture_management
    from business import innovation_management
    from business import welfare_management
    from business import accounting_tex
    #공과대학
    from engineering import chemical
    from engineering import industrial
    from engineering import electrical
    from engineering import mechanical
    from engineering import architecture
    from engineering import material
    #it대학
    from it import software
    #차세대반도체
    #자유전공
except ImportError as e:
    print(f"[Import Error] 크롤러 모듈을 찾을 수 없습니다: {e}")
    exit()

def main():
    # 1-1. 기본 저장 경로 (루트 디렉토리 기준)
    BASE_SAVE_PATH = "notices" 
    
    # 1-2. 전체 통합 파일 경로
    GLOBAL_SAVE_FILE = os.path.join(BASE_SAVE_PATH, "ssu_notices.csv")
    
    # 1-3. 크롤링 옵션
    MAX_PAGES_TO_SCAN = 100 
    UNIQUE_ID_COLUMNS = ["title", "link"]
    
    #crawler_config example
    """
        "": {
             "links_func": .get_post_links,
             "content_func": .get_post_contents,
             "save_sub_path": ".csv"
        }
        """
    CRAWLER_CONFIG = {
        # #소프트웨어학부
        "software": {
            "links_func": software.get_post_links,
            "content_func": software.get_post_contents,
            "save_sub_path": "it/software.csv"
        },
        #국제법무학과
        "globallaw": {
             "links_func": globallaw.get_post_links,
             "content_func": globallaw.get_post_contents,
             "save_sub_path": "law/globallaw.csv"
        },
        #법학과
        "law": {
             "links_func": law.get_post_links,
             "content_func": law.get_post_contents,
             "save_sub_path": "law/law.csv"
        },
        #사회복지학부
        "socialwelfare": {
             "links_func": socialwelfare.get_post_links,
             "content_func": socialwelfare.get_post_contents,
             "save_sub_path": "social_science/socialwelfare.csv"
        },
        #행정학부
        "publicadministration": {
             "links_func": publicadministration.get_post_links,
             "content_func": publicadministration.get_post_contents,
             "save_sub_path": "social_science/publicadministration.csv"
        },
        
        #정치외교학과
        "politicalscience_internationalrelations": {
             "links_func": politicalscience_internationalrelations.get_post_links,
             "content_func": politicalscience_internationalrelations.get_post_contents,
             "save_sub_path": "social_science/politicalscience_internationalrelations.csv"
        },
        #정보사회학과
        "informationsociology": {
             "links_func": informationsociology.get_post_links,
             "content_func": informationsociology.get_post_contents,
             "save_sub_path": "social_science/informationsociology.csv"
        },
        #언론홍보학과
        "journalism_publicrelation_advertising": {
             "links_func": journalism_publicrelation_advertising.get_post_links,
             "content_func": journalism_publicrelation_advertising.get_post_contents,
             "save_sub_path": "social_science/journalism_publicrelation_advertising.csv"
        },
        #평생교육학과
        "lifelong_edu": {
             "links_func": lifelong_edu.get_post_links,
             "content_func": lifelong_edu.get_post_contents,
             "save_sub_path": "social_science/lifelong_edu.csv"
        },
        #경제학과
        "economics": {
             "links_func": economics.get_post_links,
             "content_func": economics.get_post_contents,
             "save_sub_path": "economy/economics.csv"
        },
        #글로벌통상학과
        "global_commerce": {
             "links_func": global_commerce.get_post_links,
             "content_func": global_commerce.get_post_contents,
             "save_sub_path": "economy/global_commerce.csv"
        },
        #금융경제학과
        "ecofinance": {
             "links_func": ecofinance.get_post_links,
             "content_func": ecofinance.get_post_contents,
             "save_sub_path": "economy/ecofinance.csv"
        },
        #국제무역학과
        "internationaltrade_transaction": {
             "links_func": internationaltrade_transaction.get_post_links,
             "content_func": internationaltrade_transaction.get_post_contents,
             "save_sub_path": "economy/internationaltrade_transaction.csv"
        },

        #경영학부
        "business_administration": {
             "links_func": business_administration.get_post_links,
             "content_func": business_administration.get_post_contents,
             "save_sub_path": "business/business_administration.csv"
        },
        #벤처중소기업학과
        "venture_smallbusiness": {
             "links_func": venture_smallbusiness.get_post_links,
             "content_func": venture_smallbusiness.get_post_contents,
             "save_sub_path": "business/venture_smallbusiness.csv"
        },
        #회계학부
        "accounting": {
             "links_func": accounting.get_post_links,
             "content_func": accounting.get_post_contents,
             "save_sub_path": "business/accounting.csv"
        },
        #금융학부
        "finance": {
             "links_func": finance.get_post_links,
             "content_func": finance.get_post_contents,
             "save_sub_path": "business/finance.csv"
        },
        #벤처경영학과
        "venture_management": {
             "links_func": venture_management.get_post_links,
             "content_func": venture_management.get_post_contents,
             "save_sub_path": "business/venture_management.csv"
        },
        #혁신경영학과
        "innovation_management": {
             "links_func": innovation_management.get_post_links,
             "content_func": innovation_management.get_post_contents,
             "save_sub_path": "business/innovation_management.csv"
        },
        #복지경영학과
        "welfare_management": {
             "links_func": welfare_management.get_post_links,
             "content_func": welfare_management.get_post_contents,
             "save_sub_path": "business/welfare_management.csv"
        },
        #회계세무학과
        "accounting_tex": {
             "links_func": accounting_tex.get_post_links,
             "content_func": accounting_tex.get_post_contents,
             "save_sub_path": "business/accounting_tex.csv"
        },

        #화학공학과
        "chemical": {
             "links_func": chemical.get_post_links,
             "content_func": chemical.get_post_contents,
             "save_sub_path": "engineering/chemical.csv"
        },
        #산업.시스템공학과
        "industrial": {
             "links_func": industrial.get_post_links,
             "content_func": industrial.get_post_contents,
             "save_sub_path": "engineering/industrial.csv"
        },
        #전기공학부
        "electrical": {
             "links_func": electrical.get_post_links,
             "content_func": electrical.get_post_contents,
             "save_sub_path": "engineering/electrical.csv"
        },
        #기계공학부
        "mechanical": {
             "links_func": mechanical.get_post_links,
             "content_func": mechanical.get_post_contents,
             "save_sub_path": "engineering/mechanical.csv"
        },
        #건축학부
        "architecture": {
             "links_func": architecture.get_post_links,
             "content_func": architecture.get_post_contents,
             "save_sub_path": "engineering/architecture.csv"
        },
        #신소재공학과
        "material": {
             "links_func": material.get_post_links,
             "content_func": material.get_post_contents,
             "save_sub_path": "engineering/material.csv"
        },


        

    }
    driver = setup_driver()
    if driver is None:
        print("웹 드라이버 설정에 실패하여 크롤링을 종료합니다.")
        return 

    all_new_data_list = [] 

    try:
        # --- [ 2. 학과별 순차 크롤링 ] ---
        for dept_name, config in CRAWLER_CONFIG.items():
            print(f"\n=== [ {dept_name.upper()} ] 크롤링 프로세스 시작 ===")
            
            # 2-1. 경로 결합 (BASE_PATH + sub_path)
            dept_file_full_path = os.path.join(BASE_SAVE_PATH, config["save_sub_path"])
            
            # 2-2. 기존 데이터 로드
            dept_old_df, dept_old_ids = load_data(dept_file_full_path, id_columns=UNIQUE_ID_COLUMNS)

            # 2-3. 링크 수집 실행
            new_posts_list = config["links_func"](
                driver=driver,
                old_post_ids=dept_old_ids,
                max_pages_to_scan=MAX_PAGES_TO_SCAN
            )
            
            if not new_posts_list:
                print(f"--- [ {dept_name.upper()} ] 업데이트 된 게시글이 없습니다. ---")
                continue

            # 2-4. 본문 수집 실행
            new_final_data_list = config["content_func"](
                driver=driver,
                posts_metadata=new_posts_list
            )
            
            # 2-5. 학과별 파일 저장
            new_item_count = process_and_save_results(
                new_data_list=new_final_data_list,
                old_df=dept_old_df,
                filename=dept_file_full_path,
                id_columns=UNIQUE_ID_COLUMNS
            )
            
            print(f"[ {dept_name.upper()} ] 완료: {new_item_count}개 신규 게시글 저장됨.")
            
            # 2-6. 전체 통합 리스트에 추가
            all_new_data_list.extend(new_final_data_list)

        # --- [ 3. 전체 통합 파일 업데이트 ] ---
        if all_new_data_list:
            print(f"\n=== [ GLOBAL ] 전체 통합 파일 업데이트 시작 ===")
            global_old_df, _ = load_data(GLOBAL_SAVE_FILE, id_columns=UNIQUE_ID_COLUMNS)
            
            total_new_count = process_and_save_results(
                new_data_list=all_new_data_list,
                old_df=global_old_df,
                filename=GLOBAL_SAVE_FILE,
                id_columns=UNIQUE_ID_COLUMNS
            )
            print(f"[ GLOBAL ] 완료: 총 {total_new_count}개 신규 게시글이 통합 파일에 추가됨.")
        else:
            print("\n=== [ GLOBAL ] 모든 학과가 최신 상태입니다. ===")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] 메인 프로세스 중단: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n브라우저를 종료했습니다.")

if __name__ == "__main__":
    main()