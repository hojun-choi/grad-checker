from utility import *

# --- [Business Administration] 설정 ---
DEPARTMENT = "business_administration"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    BASE_URL = "https://biz.ssu.ac.kr"
    BASE_URL_TEMPLATE = "https://biz.ssu.ac.kr/bbs/list.do?bId=BBS_03_NOTICE&page={page_num}"
    
    # 테이블(tr)이 아닌 리스트(li) 구조
    LIST_ROW_SELECTOR = "#bList01 > li"
    TITLE_SELECTOR = "div:first-child a"
    # 날짜와 작성자가 "2025-11-07 / 숭실대 경영학부" 형태로 묶여 있음
    INFO_SELECTOR = "div:last-child > span"
    
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
                link = BASE_URL + link_relative
                
                # 고유 ID를 (title, link)로 변경
                post_id = (title, link) 
                
                # 공지 여부 확인 ('fixedPost' 클래스)
                is_notice = "fixedPost" in title_element.get("class", [])

                if post_id in old_post_ids:
                    if is_notice:
                        # 이미 수집한 '공지'는 건너뛰기 (페이지에 고정되어 있으므로)
                        continue
                    else:
                        # 이미 수집한 '일반' 글을 만나면 크롤링 중단
                        stop_crawling = True
                        break

                # 날짜 및 작성자 파싱
                info_element = row.select_one(INFO_SELECTOR)
                if info_element:
                    info_text = info_element.text.strip()
                    # "2025-11-07 / 숭실대 경영학부" 형식 분리
                    if "/" in info_text:
                        date_part, author_part = info_text.split("/", 1)
                        date = date_part.strip()
                        author = author_part.strip()
                    else:
                        date = info_text.strip()
                        author = "N/A"
                else:
                    date = "N/A"
                    author = "N/A"

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
    # 게시글 본문 ID
    CONTENT_SELECTOR = "#postContents" 
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        
        try:
            soup = get_soup(driver, link, delay=3.0) 
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