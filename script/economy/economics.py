from utility import *

# --- [Economics] 설정 ---
DEPARTMENT = "economics"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    BASE_URL_TEMPLATE = "https://eco.ssu.ac.kr/bbs/board.php?bo_table=notice&page={page_num}"
    LIST_ROW_SELECTOR = ".tbl_head01 tbody tr"
    NOTICE_SELECTOR = ".notice_icon"
    NUM_SELECTOR = ".td_num2"
    TITLE_SELECTOR = ".td_subject .bo_tit a" # 제목 링크가 .bo_tit 안에 있음
    AUTHOR_SELECTOR = ".td_name"
    DATE_SELECTOR = ".td_datetime"
    
    new_posts_metadata = []
    seen_notice_titles = set()
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: break
                
            url = BASE_URL_TEMPLATE.format(page_num=page_num)
            
            soup = get_soup(driver, url, delay=0.5) 
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print("게시글이 없어 1단계를 종료합니다.")
                break
                
            for row in rows:
                # 행 안에 제목 요소가 없으면 건너뜀 (헤더 등)
                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element: continue
                
                title = title_element.text.strip()
                link = title_element['href']
                
                # 고유 ID를 (title, link)로 변경
                post_id = (title, link) 
                
                if post_id in old_post_ids:
                    stop_crawling = True
                    break

                # 공지 여부 확인
                is_notice = bool(row.select_one(NOTICE_SELECTOR))
                
                author = row.select_one(AUTHOR_SELECTOR).text.strip()
                date_text = row.select_one(DATE_SELECTOR).text.strip()
                
                # 날짜 표준화 (MM-DD 형식이라 그대로 둠, 필요시 연도 추가 로직 필요)
                date = date_text

                # 새 형식에 맞게 데이터 구성
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                if is_notice:
                    if title not in seen_notice_titles:
                        new_posts_metadata.append(post_data)
                        seen_notice_titles.add(title)
                else:
                    new_posts_metadata.append(post_data)

            time.sleep(0.3) 

    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    CONTENT_SELECTOR = "#bo_v_con" 
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        
        try:
            soup = get_soup(driver, link, delay=0.5) 
            content_element = soup.select_one(CONTENT_SELECTOR)
            
            if content_element:
                content_text = content_element.get_text(separator="\n", strip=True)
            else:
                content_text = "[본문 내용을 찾을 수 없습니다]"
                
            post['content'] = content_text

        except Exception as e:
            print(f" 	[에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata