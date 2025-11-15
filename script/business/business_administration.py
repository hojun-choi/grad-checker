from utility import *

# --- [Business Administration] 설정 ---
DEPARTMENT = "business_administration"

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    """
    숭실대학교 경영학부 공지사항 게시판에서 게시글 링크와 메타데이터를 수집합니다.
    """
    
    BASE_URL = "http://biz.ssu.ac.kr"
    BASE_URL_TEMPLATE = "http://biz.ssu.ac.kr/bbs/list.do?bId=BBS_03_NOTICE&page={page_num}"
    
    # 리스트(li) 구조
    LIST_CONTAINER_SELECTOR = "#bList01"
    LIST_ROW_SELECTOR = "#bList01 > li"
    TITLE_SELECTOR = "div:first-child a"
    # 날짜와 작성자가 "2025-11-07 / 숭실대 경영학부" 형태로 묶여 있음
    INFO_SELECTOR = "div:last-child > span"
    
    new_posts_metadata = []
    seen_notice_titles = set()
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: 
                break
                
            url = BASE_URL_TEMPLATE.format(page_num=page_num)
            
            # 연결 재시도 로직 (타임아웃 대응)
            soup = None
            max_retries = 3
            for retry in range(max_retries):
                try:
                    soup = get_soup(driver, url, delay=0.5)
                    break
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"    [경고] 페이지 로드 실패 (재시도 {retry + 1}/{max_retries}): {str(e)[:50]}")
                        time.sleep(2)
                    else:
                        raise
            
            if not soup:
                print("페이지를 로드할 수 없어 1단계를 종료합니다.")
                break
                
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print("게시글이 없어 1단계를 종료합니다.")
                break
                
            for row in rows:
                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                
                # href 속성 추출
                link_relative = title_element.get('href', '')
                if not link_relative:
                    continue
                
                # 절대 경로 변환
                if link_relative.startswith('http'):
                    link = link_relative
                elif link_relative.startswith('/'):
                    link = BASE_URL + link_relative
                else:
                    link = BASE_URL + '/' + link_relative
                
                # 고유 ID 생성
                post_id = (title, link) 
                
                # 중복 검사
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                # 날짜 및 작성자 파싱
                info_element = row.select_one(INFO_SELECTOR)
                    
                if info_element:
                    info_text = info_element.text.strip()
                    # "2025-11-10 / 숭실대 경영학부" 형식 분리
                    if "/" in info_text:
                        parts = info_text.split("/")
                        date = parts[0].strip()
                        author = parts[1].strip() if len(parts) > 1 else "경영학부"
                    else:
                        date = info_text.strip()
                        author = "경영학부"
                else:
                    date = "날짜 없음"
                    author = "경영학부"

                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                # 공지글 여부 확인 (class에 fixedPost 포함 여부)
                # HTML 구조상 공지글은 없는 것으로 보임
                is_notice = False
                
                if is_notice:
                    if title not in seen_notice_titles:
                        new_posts_metadata.append(post_data)
                        seen_notice_titles.add(title)
                else:
                    new_posts_metadata.append(post_data)

            time.sleep(0.3) 

    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata


def get_post_contents(driver, posts_metadata):
    """
    수집된 게시글 메타데이터(링크)를 바탕으로 각 게시글의 본문 내용을 수집합니다.
    """
    
    CONTENT_SELECTOR = "#postContents" 
    
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
            print(f"    [에러] '{post['title'][:30]}...' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata