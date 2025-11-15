from utility import *
import re


# --- [Media] 설정 ---
DEPARTMENT = "global_media"

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    """
    숭실대학교 글로벌미디어학부 공지사항 게시판에서 게시글 링크와 메타데이터를 수집합니다.
    Next.js 기반 사이트로 동적 로딩이 필요합니다.
    """
    
    # 글로벌미디어학부 공지사항 URL 템플릿
    BASE_URL_TEMPLATE = "https://media.ssu.ac.kr/board/notices?page={page_num}"
    BASE_DOMAIN = "https://media.ssu.ac.kr"
    
    new_posts_metadata = []
    seen_notice_titles = set()
    stop_crawling = False
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling: 
                break
                
            url = BASE_URL_TEMPLATE.format(page_num=page_num)
            
            # 동적 페이지 로딩을 위해 대기 시간 증가
            soup = get_soup(driver, url, delay=3.0)
            
            # Next.js 앱이 로드될 때까지 추가 대기
            time.sleep(2)
            
            # 페이지 소스 다시 가져오기 (JavaScript 실행 후)
            from bs4 import BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 게시글 추출 시도 (여러 선택자 사용)
            # Next.js 사이트의 일반적인 구조
            posts = []
            
            # 선택자 옵션들
            selectors = [
                'article',
                'div[class*="post"]',
                'div[class*="item"]',
                'div[class*="card"]',
                'li[class*="post"]',
                'a[href*="/board/notices/"]',
                'a[href*="/post/"]'
            ]
            
            for selector in selectors:
                posts = soup.select(selector)
                if posts and len(posts) > 0:
                    print(f"  '{selector}' 선택자로 {len(posts)}개 항목 발견")
                    break
            
            if not posts:
                # 게시글을 찾지 못한 경우, 페이지 내용 확인
                print("  게시글을 찾을 수 없습니다. 페이지 구조 확인 중...")
                
                # 모든 링크 확인
                all_links = soup.find_all('a', href=True)
                notice_links = [link for link in all_links if 'notices' in link.get('href', '')]
                
                if notice_links:
                    print(f"  공지사항 관련 링크 {len(notice_links)}개 발견")
                    posts = notice_links
                else:
                    print("  게시글이 없어 1단계를 종료합니다.")
                    break
            
            has_regular_post = False

            has_regular_post = False

            for post in posts:
                # 링크 추출
                if post.name == 'a':
                    link = post.get('href', '')
                    title_element = post
                else:
                    link_element = post.select_one('a')
                    if not link_element:
                        continue
                    link = link_element.get('href', '')
                    title_element = link_element
                
                # 제목 추출
                title = title_element.get_text(strip=True)
                
                # 제목이 너무 짧거나 없으면 스킵
                if not title or len(title) < 3:
                    continue
                
                # 상대 경로를 절대 경로로 변환
                if link and not link.startswith('http'):
                    if link.startswith('/'):
                        link = BASE_DOMAIN + link
                    else:
                        link = BASE_DOMAIN + '/' + link
                
                if not link or 'notices' not in link:
                    continue
                
                # 고유 ID 생성
                post_id = (title, link)
                
                # 중복 검사
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                # 날짜와 작성자 추출 시도
                date = "날짜 없음"
                author = "글로벌미디어학부"
                
                # 날짜 패턴 찾기
                date_patterns = [
                    r'\d{4}[-./]\d{1,2}[-./]\d{1,2}',
                    r'\d{4}\.\s*\d{1,2}\.\s*\d{1,2}',
                    r'\d{2}[-./]\d{1,2}[-./]\d{1,2}'
                ]
                
                post_text = post.get_text()
                for pattern in date_patterns:
                    date_match = re.search(pattern, post_text)
                    if date_match:
                        date = date_match.group(0)
                        break
                
                post_data = {
                    "department": DEPARTMENT,
                    "title": title,
                    "author": author,
                    "date": date,
                    "link": link
                }
                
                # 공지글 구분 (일단 모두 일반글로 처리)
                new_posts_metadata.append(post_data)
                has_regular_post = True

            # 게시글이 없으면 마지막 페이지
            if not has_regular_post:
                print("  더 이상 게시글이 없어 마지막 페이지로 간주합니다.")
                break
                
            time.sleep(1.0)  # 페이지 간 대기
            
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
            # 동적 페이지 로딩
            soup = get_soup(driver, link, delay=3.0)
            time.sleep(2)
            
            # 페이지 소스 다시 가져오기
            from bs4 import BeautifulSoup
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            content_text = None
            
            # 본문 선택자들
            content_selectors = [
                'article',
                'div[class*="content"]',
                'div[class*="post"]',
                'div[class*="body"]',
                'main article',
                'main div'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    # script, style 제거
                    for tag in content_element.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        tag.decompose()
                    
                    content_text = content_element.get_text(separator="\n", strip=True)
                    
                    if content_text and len(content_text) > 50:
                        break
            
            if not content_text or len(content_text) < 50:
                # body 전체에서 추출
                body = soup.select_one('body')
                if body:
                    for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer']):
                        tag.decompose()
                    content_text = body.get_text(separator="\n", strip=True)
                else:
                    content_text = "[본문 내용을 찾을 수 없습니다]"
            
            post['content'] = content_text
            
        except Exception as e:
            print(f"    [에러] '{post['title'][:30]}...' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(1.0)  # 게시글 간 대기
            
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata