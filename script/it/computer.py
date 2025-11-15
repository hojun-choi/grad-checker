from utility import *

# --- [Computer] 설정 ---
DEPARTMENT = "computer"

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    """
    숭실대학교 컴퓨터학부 공지사항 게시판에서 게시글 링크와 메타데이터를 수집합니다.
    (sw.ssu.ac.kr 과 HTML 구조가 동일하여 로직을 그대로 사용합니다.)
    """
    
    # 컴퓨터학부 공지사항 URL 템플릿
    BASE_URL_TEMPLATE = "https://cse.ssu.ac.kr/bbs/board.php?bo_table=notice&page={page_num}"
    
    # software.py 와 선택자가 동일합니다.
    LIST_ROW_SELECTOR = "#bo_list tbody > tr"
    NOTICE_SELECTOR = ".bo_notice"
    TITLE_SELECTOR = ".td_subject a"
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
        
            # get_soup 함수는 utility.py에 정의되어 있다고 가정합니다.
            soup = get_soup(driver, url, delay=0.5) 
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print("게시글이 없어 1단계를 종료합니다.")
                break
                
            has_regular_post = False

            for row in rows:
                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element: continue
                
                title = title_element.text.strip()
                # href 속성을 가져와 완전한 URL로 만듭니다. (utility.py에 관련 기능이 있을 수 있으나,
                # 예시 코드에는 절대 경로로 이미 링크가 제공되므로 그대로 사용합니다)
                link = title_element['href']
                
                # 고유 ID 생성 (제목과 링크로 구성)
                post_id = (title, link) 
                
                # --- 중복 검사 ---
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                author = row.select_one(AUTHOR_SELECTOR).text.strip()
                date = row.select_one(DATE_SELECTOR).text.strip()
                
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                # 공지글인지 일반글인지 확인
                is_notice = bool(row.select_one(NOTICE_SELECTOR))
                if is_notice:
                    # 공지글이면서, 아직 추가되지 않은 제목인 경우
                    if title not in seen_notice_titles:
                        new_posts_metadata.append(post_data)
                        seen_notice_titles.add(title)
                else:
                    # 일반글
                    new_posts_metadata.append(post_data)
                    has_regular_post = True

            # 첫 페이지만 스캔한 게 아니고, 일반 게시글이 없다면(공지글만 있다면) 마지막 페이지로 간주
            if not has_regular_post and page_num > 1:
                print("공지글 외에 일반 게시글이 없어 마지막 페이지로 간주합니다.")
                break
                
            time.sleep(0.3) # 페이지 간 예의상의 딜레이
            
    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    """
    수집된 게시글 메타데이터(링크)를 바탕으로 각 게시글의 본문 내용을 수집합니다.
    (sw.ssu.ac.kr 과 HTML 구조가 동일하여 로직을 그대로 사용합니다.)
    """
    
    # software.py 와 본문 선택자가 동일합니다.
    CONTENT_SELECTOR = "#bo_v_con" 
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
            # get_soup 함수는 utility.py에 정의되어 있다고 가정합니다.
            soup = get_soup(driver, link, delay=0.5)
            content_element = soup.select_one(CONTENT_SELECTOR)
            
            if content_element:
                # 본문 텍스트 추출 (줄바꿈 유지, 양끝 공백 제거)
                content_text = content_element.get_text(separator="\n", strip=True)
            else:
                content_text = "[본문 내용을 찾을 수 없습니다]"
                
            post['content'] = content_text
            
        except Exception as e:
            print(f"    [에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) # 게시글 간 예의상의 딜레이
            
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata