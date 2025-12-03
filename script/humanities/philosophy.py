from utility import *

# --- [Philosophy] 설정 ---
DEPARTMENT = "philosophy"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    # 철학과 공지사항 페이지네이션 URL 구조
    # 한글 경로: https://philo.ssu.ac.kr/학과사무실알림/공지사항/page/{page_num}/?term_id
    BASE_URL_TEMPLATE = "https://philo.ssu.ac.kr/%ed%95%99%ea%b3%bc%ec%82%ac%eb%ac%b4%ec%8b%a4%ec%95%8c%eb%a6%bc/%ea%b3%b5%ec%a7%80%ec%82%ac%ed%95%ad/page/{page_num}/?term_id"
    
    # HTML 소스 분석에 따른 선택자 설정
    LIST_ROW_SELECTOR = ".baord_table tbody > tr"
    NUM_SELECTOR = "td:nth-of-type(1)"
    TITLE_SELECTOR = "td.title a"
    DATE_SELECTOR = "td:nth-of-type(4)" # 번호, 제목, 파일, '등록일', 조회수 순서

    new_posts_metadata = []
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling:
                break
                
            url = BASE_URL_TEMPLATE.format(page_num=page_num)
            
            soup = get_soup(driver, url, delay=0.5) 
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print("게시글이 없어 1단계를 종료합니다.")
                break
                
            for row in rows:
                num_cell = row.select_one(NUM_SELECTOR)
                title_element = row.select_one(TITLE_SELECTOR)
                date_cell = row.select_one(DATE_SELECTOR)

                # 필수 요소가 없으면 건너뜀
                if not num_cell or not title_element or not date_cell:
                    continue

                title = title_element.text.strip()
                link = title_element['href']
                date = date_cell.text.strip()

                # 고유 ID를 (title, link)로 변경
                post_id = (title, link) 
                
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                # 새 형식에 맞게 데이터 구성
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": "N/A", # 철학과 목록에도 작성자 정보 없음
                    "date": date,
                    "link": link,
                }
                
                new_posts_metadata.append(post_data)

            time.sleep(0.3)

    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    # HTML 소스 분석 결과 본문은 div.td_box 안에 있음
    CONTENT_SELECTOR = "div.td_box" 
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
            soup = get_soup(driver, link, delay=0.5) 
            content_element = soup.select_one(CONTENT_SELECTOR)
            
            if content_element:
                content_text = content_element.get_text(separator="\n", strip=True)
            else:
                content_text = "[본문 내용을 찾을 수 없습니다]"
                
            post['content'] = content_text 

        except Exception as e:
            print(f"    [에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata