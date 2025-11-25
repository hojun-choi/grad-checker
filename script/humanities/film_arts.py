import json
from utility import *

# --- [Film Arts] 설정 ---
DEPARTMENT = "film_arts"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    # 영화예술전공은 HTML 파싱이 아닌 JSON API를 호출해야 함
    # LastNoticeIndex를 갱신하며 다음 리스트를 가져오는 구조
    BASE_API_URL = "https://film.ssu.ac.kr/notice/notice_list?LastNoticeIndex={}"
    
    new_posts_metadata = []
    stop_crawling = False
    last_notice_index = 0 # 첫 페이지는 0으로 시작
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 (JSON API) ---")

    try:
        for page_num in range(1, max_pages_to_scan + 1):
            if stop_crawling:
                break
                
            # 페이지 번호 대신 last_notice_index를 사용하여 URL 생성
            url = BASE_API_URL.format(last_notice_index)
            
            # 브라우저로 JSON 응답 페이지를 엽니다.
            soup = get_soup(driver, url, delay=0.5)
            
            # soup.text에 JSON 문자열이 담겨있음
            try:
                response_json = json.loads(soup.text)
                posts = response_json.get('data_list', [])
            except ValueError:
                print("JSON 파싱 실패. API 응답을 확인하세요.")
                break
            
            if not posts:
                print("더 이상 게시글이 없어 1단계를 종료합니다.")
                break
                
            for post in posts:
                # JSON 필드 추출 (HTML 소스 내 make_notice_html 함수 참조)
                notice_index = post.get('NoticeIndex')
                title = post.get('Title', '').strip()
                category = post.get('Category', '')
                
                # 목록 API에는 날짜 정보가 명시되어 있지 않음 (상세에서 확인 필요)
                date = "N/A" 
                
                # 상세 페이지(API) 링크 구성
                link = f"https://film.ssu.ac.kr/notice/notice_view?NoticeIndex={notice_index}"

                # 제목에 카테고리 포함
                full_title = f"[{category}] {title}" if category else title

                post_id = (full_title, link)
                
                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{full_title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break

                post_data = {
                    "department": DEPARTMENT,
                    "title": full_title,
                    "author": "N/A",
                    "date": date, # 2단계에서 업데이트 시도
                    "link": link,
                    "custom_id": notice_index # 다음 페이지 로딩을 위한 ID 저장
                }
                
                new_posts_metadata.append(post_data)
                
                # 다음 페이지 로딩을 위해 마지막 인덱스 업데이트
                last_notice_index = notice_index

            time.sleep(0.3)

    except Exception as e:
        print(f"[에러] {DEPARTMENT} 게시글 목록 수집 중 오류 발생: {e}")
        
    print(f"--- [{DEPARTMENT}] 1단계 완료. 총 {len(new_posts_metadata)}개의 *새로운* 게시글 수집 ---")
    return new_posts_metadata

def get_post_contents(driver, posts_metadata):
    
    print(f"\n--- [{DEPARTMENT}] 2단계: {len(posts_metadata)}개 새 게시글 본문 수집 시작 ---")

    if not posts_metadata:
        print(f"--- [{DEPARTMENT}] 2단계: 수집할 새 본문이 없습니다. ---")
        return []

    for i, post in enumerate(posts_metadata):
        link = post['link']
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
            # JSON API 호출
            soup = get_soup(driver, link, delay=0.5)
            
            response_json = json.loads(soup.text)
            data_modify = response_json.get('data_modify', {})
            
            if data_modify:
                # HTML 태그가 포함된 본문 내용
                content_html = data_modify.get('Content', '')
                
                # HTML 태그 제거 및 텍스트 추출을 위해 BeautifulSoup 객체 생성
                content_soup = BeautifulSoup(content_html, 'html.parser')
                content_text = content_soup.get_text(separator="\n", strip=True)
                
                # API 상세 데이터에 등록일(RegDate)이 있다면 업데이트 (소스상 확인되진 않으나 일반적 추정)
                if 'RegDate' in data_modify:
                    post['date'] = data_modify['RegDate']
                
                # 파일 정보가 있다면 추가
                if data_modify.get('OrgFile'):
                    content_text += f"\n\n[첨부파일: {data_modify['OrgFile']}]"

            else:
                content_text = "[본문 내용을 찾을 수 없습니다]"
                
            post['content'] = content_text 

        except Exception as e:
            print(f"    [에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata