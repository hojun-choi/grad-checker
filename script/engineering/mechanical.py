from utility import *

# --- [Mechanical Engineering] 설정 ---
DEPARTMENT = "mechanical"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    BASE_URL = "http://me.ssu.ac.kr"
    BASE_URL_TEMPLATE = "http://me.ssu.ac.kr/notice/notice01.php?page={page_num}"
    
    LIST_ROW_SELECTOR = ".board-list tbody tr"
    NUM_SELECTOR = ".w_cell"
    TITLE_SELECTOR = ".subject a"
    # 작성자가 3번째 td, 날짜가 4번째 td
    AUTHOR_SELECTOR = "td:nth-of-type(3)"
    DATE_SELECTOR = "td:nth-of-type(4)"
    
    new_posts_metadata = []
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
                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element: continue
                
                title = title_element.text.strip()
                
                # 상대 경로를 절대 경로로 변환
                link_relative = title_element['href']
                if link_relative.startswith("/"):
                    link = BASE_URL + link_relative
                else:
                    link = link_relative

                # 고유 ID를 (title, link)로 변경
                post_id = (title, link) 
                
                if post_id in old_post_ids:
                    stop_crawling = True
                    break

                # 공지 여부 확인 (.ico 클래스 또는 텍스트 '공지' 확인)
                num_element = row.select_one(NUM_SELECTOR)
                is_notice = False
                if num_element:
                    if num_element.select_one(".ico") or "공지" in num_element.text:
                         is_notice = True

                author = row.select_one(AUTHOR_SELECTOR).text.strip()
                date_text = row.select_one(DATE_SELECTOR).text.strip()
                
                try:
                    date = date_text.replace(".", "-")
                except Exception:
                    date = date_text

                # 새 형식에 맞게 데이터 구성
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                new_posts_metadata.append(post_data)

            time.sleep(0.3) 

    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    CONTENT_SELECTOR = ".view_con" 
    
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