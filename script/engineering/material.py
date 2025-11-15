from utility import *

# --- [Materials Science and Engineering] 설정 ---
DEPARTMENT = "materials"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    BASE_URL = "https://materials.ssu.ac.kr"
    BASE_URL_TEMPLATE = "https://materials.ssu.ac.kr/bbs/board.php?tbl=bbs51&page={page_num}"
    
    # 테이블이 아닌 ul > li 구조의 리스트 게시판
    LIST_ROW_SELECTOR = ".news-list ul li"
    TITLE_SELECTOR = ".tit_box strong"
    DATE_SELECTOR = ".mob_date"
    # 작성자 정보는 목록에 없음
    
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
                link_element = row.select_one("a")
                if not link_element: continue
                
                # 상대 경로를 절대 경로로 변환
                link_relative = link_element['href']
                link = BASE_URL + link_relative

                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element: continue

                # '공지' 태그 확인 및 제목에서 제거
                notice_tag = title_element.select_one(".tag01")
                is_notice = False
                if notice_tag:
                    is_notice = True
                    notice_tag.decompose() # 태그 제거하여 순수 제목만 추출

                title = title_element.text.strip()
                
                # 고유 ID를 (title, link)로 변경
                post_id = (title, link) 
                
                if post_id in old_post_ids:
                    stop_crawling = True
                    break

                date = row.select_one(DATE_SELECTOR).text.strip()

                # 새 형식에 맞게 데이터 구성
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": "N/A", 
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
    # 본문 선택자 (실제 상세 페이지 확인 필요, 임시로 일반적인 클래스 사용)
    CONTENT_SELECTOR = ".view_box" 
    
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
                # 다른 선택자 시도 (필요시 추가)
                content_text = "[본문 내용을 찾을 수 없습니다]"
                
            post['content'] = content_text

        except Exception as e:
            print(f" 	[에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata