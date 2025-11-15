from utility import *

# --- [SSU Main (SSU:catch)] 설정 ---
DEPARTMENT = "ssu_main"
BASE_DOMAIN = "https://scatch.ssu.ac.kr" # 숭실대학교 SSU:catch

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    """
    숭실대학교 SSU:catch 공지사항 (학사) 게시판에서 게시글 링크와 메타데이터를 수집합니다.
    """
    
    # SSU:catch 학사 공지 URL 템플릿
    # 1페이지는 URL이 다릅니다.
    URL_PAGE_1 = "https://scatch.ssu.ac.kr/%ea%b3%b5%ec%a7%80%ec%82%ac%ed%95%ad/?f&category=%ED%95%99%EC%82%AC&keyword"
    BASE_URL_TEMPLATE = "https://scatch.ssu.ac.kr/%ea%b3%b5%ec%a7%80%ec%82%ac%ed%95%ad/page/{page_num}/?f&category=%ED%95%99%EC%82%AC&keyword"
    
    # CSS 선택자
    LIST_ROW_SELECTOR = "ul.notice-lists > li:not(.notice_head)"
    TITLE_SELECTOR = "div.notice_col3 a"
    AUTHOR_SELECTOR = "div.notice_col4"
    DATE_SELECTOR = "div.notice_col1" # '2025.11.14' 텍스트 포함
    
    # 이 게시판은 '공지' 구분이 따로 없습니다.
    
    new_posts_metadata = []
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: break
            
            # 1페이지와 2페이지 이상의 URL 형식이 다름
            if page_num == 1:
                url = URL_PAGE_1
            else:
                url = BASE_URL_TEMPLATE.format(page_num=page_num)
        
            # get_soup 함수는 utility.py에 정의되어 있다고 가정합니다.
            soup = get_soup(driver, url, delay=0.5) 
            rows = soup.select(LIST_ROW_SELECTOR)
            
            if not rows:
                print(f"페이지 {page_num}에 게시글이 없어 1단계를 종료합니다.")
                break
                
            for row in rows:
                title_element = row.select_one(TITLE_SELECTOR)
                if not title_element: continue
                
                # 제목 텍스트만 추출 (span 태그 안의 텍스트)
                title_span = title_element.find("span", class_="d-inline-blcok")
                title = title_span.text.strip() if title_span else title_element.text.strip()
                
                # 링크가 절대 경로로 제공됨
                link = title_element.get('href')
                if not link: continue
                
                # 고유 ID 생성 (제목과 링크로 구성)
                post_id = (title, link) 
                
                # --- 중복 검사 ---
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                author_element = row.select_one(AUTHOR_SELECTOR)
                author = author_element.text.strip() if author_element else "SSU:catch"
                
                date_element = row.select_one(DATE_SELECTOR)
                date_text = date_element.text.strip()
                # '2025.11.14' 형식을 '2025-11-14'로 변경
                date = date_text.replace('.', '-') if date_text else "날짜 없음"
                
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                new_posts_metadata.append(post_data)

            if stop_crawling:
                break
                
            time.sleep(0.3) # 페이지 간 예의상의 딜레이
            
    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    """
    수집된 게시글 메타데이터(링크)를 바탕으로 각 게시글의 본문 내용을 수집합니다.
    """
    
    # 본문 CSS 선택자 (h1, hr 태그 이후의 div)
    CONTENT_SELECTOR = "div.bg-white.p-4.mb-5 > div:last-of-type" 
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        
        if not link.startswith('http'):
            print(f"    [경고] '{post['title']}'의 링크가 상대 경로입니다: {link}. 건너뜁니다.")
            post['content'] = f"[수집 오류: 상대 경로 링크 ({link})]"
            continue
            
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
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