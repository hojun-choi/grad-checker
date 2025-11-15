from utility import *
import re

# --- [Electronics] 설정 ---
DEPARTMENT = "electronic_engineering"

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    """
    숭실대학교 전자정보공학부 공지사항 게시판에서 게시글 링크와 메타데이터를 수집합니다.
    주의: 이 사이트는 DB 오류가 발생할 수 있으므로 재시도 로직 포함
    """
    
    # 전자정보공학부 학사 공지사항 URL 템플릿
    # 첫 번째 문서에서 확인된 실제 URL 구조 사용
    BASE_URL_TEMPLATE = "http://infocom.ssu.ac.kr/kor/notice/undergraduate.php?pNo={page_num}&code=notice"
    BASE_DOMAIN = "http://infocom.ssu.ac.kr"
    
    new_posts_metadata = []
    seen_notice_titles = set()
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: 
                break
                
            url = BASE_URL_TEMPLATE.format(page_num=page_num)

        
            # 페이지 로드 재시도 (DB 오류 대응)
            soup = None
            max_retries = 3
            for retry in range(max_retries):
                try:
                    soup = get_soup(driver, url, delay=1.0)
                    
                    # Fatal error 체크
                    page_text = soup.get_text()
                    if "Fatal error" in page_text or "PDOException" in page_text:
                        print(f"  [경고] 서버 오류 감지 (재시도 {retry + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                    break
                except Exception as e:
                    print(f"  [경고] 페이지 로드 실패 (재시도 {retry + 1}/{max_retries}): {e}")
                    time.sleep(2)
            
            if not soup:
                print(f"  [오류] 페이지 {page_num} 로드 실패. 다음 페이지로 이동합니다.")
                continue
            
            # HTML 구조에 따른 게시글 추출
            # <a class="con_box" href="..."> 구조
            posts = soup.select('a.con_box')
            
            if not posts:
                # 대체 선택자 시도
                posts = soup.select('.list_box a')
                
            if not posts:
                print(f"게시글이 없어 1단계를 종료합니다.")
                break
            
            for post in posts:
                # 제목 추출
                title_span = post.select_one('.subject span')
                if not title_span:
                    title_span = post.select_one('.subject')
                    
                if not title_span:
                    continue
                
                title = title_span.get_text(strip=True)
                
                # 링크 추출
                link = post.get('href', '')
                if link:
                    # 상대 경로를 절대 경로로 변환
                    if link.startswith('/'):
                        link = BASE_DOMAIN + link
                    elif not link.startswith('http'):
                        # /kor/notice/... 형태로 시작하지 않는 경우
                        if not link.startswith('/kor/'):
                            link = BASE_DOMAIN + '/kor/notice/' + link
                        else:
                            link = BASE_DOMAIN + link
                else:
                    print(f"  [경고] '{title[:30]}...' 링크를 찾을 수 없습니다.")
                    continue
                
                # 고유 ID 생성
                post_id = (title, link)
                
                # 중복 검사
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                # 날짜와 조회수 추출
                info_items = post.select('.info li')
                date = "날짜 없음"
                views = "0"
                
                for item in info_items:
                    item_text = item.get_text(strip=True)
                    # 날짜 형식: 2025. 11. 03
                    if re.match(r'\d{4}\.\s*\d{1,2}\.\s*\d{1,2}', item_text):
                        date = item_text
                    # 조회수는 숫자만
                    elif item_text.isdigit():
                        views = item_text
                
                author = "전자정보공학부"
                
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "views": views,
                    "link": link
                }
                
                # 공지글 확인 (subject에 on 클래스)
                subject_div = post.select_one('.subject')
                is_notice = subject_div and 'on' in subject_div.get('class', [])
                
                if is_notice:
                    if title not in seen_notice_titles:
                        new_posts_metadata.append(post_data)
                        seen_notice_titles.add(title)
                else:
                    new_posts_metadata.append(post_data)
                
            time.sleep(0.5)  # 서버 부하 방지
            
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
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
            # 재시도 로직 (서버 오류 대응)
            soup = None
            max_retries = 3
            
            for retry in range(max_retries):
                try:
                    soup = get_soup(driver, link, delay=1.0)
                    
                    # Fatal error 체크
                    page_text = soup.get_text()
                    if "Fatal error" in page_text or "PDOException" in page_text:
                        print(f"    [경고] 서버 오류 감지 (재시도 {retry + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                    break
                except Exception as e:
                    print(f"    [경고] 본문 로드 실패 (재시도 {retry + 1}/{max_retries}): {e}")
                    time.sleep(2)
            
            if not soup:
                post['content'] = "[페이지 로드 실패]"
                continue
            
            # 본문 선택자들 시도
            content_text = None
            content_selectors = [
                '.view_content',
                '.content_box',
                '#content',
                '.board_view .content',
                'article',
                '.view_box'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # script, style 제거
                    for tag in content_element.find_all(['script', 'style']):
                        tag.decompose()
                    
                    content_text = content_element.get_text(separator="\n", strip=True)
                    
                    if content_text and len(content_text) > 20:
                        break
            
            if not content_text or len(content_text) < 20:
                content_text = "[본문 내용을 찾을 수 없습니다]"
            
            post['content'] = content_text
            
        except Exception as e:
            print(f"    [에러] '{post['title'][:30]}...' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.5)  # 서버 부하 방지
            
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata