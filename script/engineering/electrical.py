from utility import *

# --- [Electrical Engineering] 설정 ---
DEPARTMENT = "electrical"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    BASE_URL = "http://ee.ssu.ac.kr"
    # offset 기반 페이징 (10개 단위)
    BASE_URL_TEMPLATE = "http://ee.ssu.ac.kr/sub/sub05_01.php?boardid=notice&sk=&sw=&category=&offset={offset}"
    
    # 테이블이 아닌 ul > li 구조임
    LIST_ROW_SELECTOR = ".board-list2 ul li"
    NUM_SELECTOR = ".num"
    TITLE_SELECTOR = ".subject a"
    AUTHOR_SELECTOR = ".info .name"
    DATE_SELECTOR = ".info .date"
    
    new_posts_metadata = []
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: break
                
            # offset 계산 (1페이지=0, 2페이지=10, 3페이지=20 ...)
            offset = (page_num - 1) * 10
            url = BASE_URL_TEMPLATE.format(offset=offset)
            
            soup = get_soup(driver, url, delay=0.5) 
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print("게시글이 없어 1단계를 종료합니다.")
                break
                
            for row in rows:
                # 헤더나 비어있는 행 제외
                if not row.select_one(TITLE_SELECTOR):
                    continue

                title_element = row.select_one(TITLE_SELECTOR)
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

                # 공지 여부 확인 ([Notice] 텍스트 또는 li.label 클래스)
                num_text = row.select_one(NUM_SELECTOR).text.strip()
                is_notice = "[Notice]" in num_text or "label" in row.get("class", [])

                author = row.select_one(AUTHOR_SELECTOR).text.strip()
                date_text = row.select_one(DATE_SELECTOR).text.strip()
                
                # 날짜 형식 표준화 (YYYY.MM.DD -> YYYY-MM-DD)
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
    CONTENT_SELECTOR = ".board-view .body" 
    
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