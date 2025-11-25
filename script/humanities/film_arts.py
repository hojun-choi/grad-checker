import json
from utility import *

# --- [Film Arts: 영화예술전공] 설정 ---
DEPARTMENT = "film_arts"
# ---

def get_post_links(driver, old_post_ids, max_pages_to_scan):
    
    # 도메인을 'ssfilm.ssu.ac.kr'로 수정 (HTML 하단 이메일 ssfilm@ssu.ac.kr 참조)
    BASE_DOMAIN = "http://ssfilm.ssu.ac.kr"
    
    # 목록 API URL (LastNoticeIndex를 변경하며 호출)
    LIST_API_URL = f"{BASE_DOMAIN}/notice/notice_list?LastNoticeIndex={{}}"
    
    new_posts_metadata = []
    stop_crawling = False
    last_notice_index = 0 # 초기값 0
    
    print(f"--- [{DEPARTMENT}] 1단계: 새로운 게시글 목록 수집 시작 (JSON API) ---")

    try:
        # 페이지 번호 개념이 없지만, max_pages_to_scan 횟수만큼 반복해서 더 불러옵니다.
        for loop_count in range(max_pages_to_scan):
            if stop_crawling:
                break
                
            url = LIST_API_URL.format(last_notice_index)
            print(f"    API 호출: {url}")
            
            # 1. JSON 데이터 요청
            # API는 HTML이 아닌 JSON 텍스트를 반환하므로 get_soup을 쓰고 text를 파싱합니다.
            soup = get_soup(driver, url, delay=1.0)
            
            # 크롬이 JSON을 <pre> 태그로 감싸서 보여주는 경우 대비
            if soup.find("pre"):
                json_str = soup.find("pre").text
            else:
                json_str = soup.text
                
            try:
                data = json.loads(json_str)
                post_list = data.get('data_list', [])
            except ValueError:
                print("    [에러] JSON 파싱 실패. 응답 내용이 올바르지 않습니다.")
                break
            
            if not post_list:
                print("    더 이상 가져올 게시글이 없습니다.")
                break
                
            # 2. 데이터 파싱
            for post in post_list:
                notice_index = post.get('NoticeIndex')
                title = post.get('Title', '').strip()
                category = post.get('Category', '')
                
                # 목록 API에는 날짜(RegDate) 필드가 명시적으로 보이지 않음 (필요시 2단계에서 확인)
                date = "N/A" 
                
                # 전체 제목 구성
                full_title = f"[{category}] {title}" if category else title
                
                # 상세 보기 API 주소
                content_link = f"{BASE_DOMAIN}/notice/notice_view?NoticeIndex={notice_index}"
                
                post_id = (full_title, content_link)

                if post_id in old_post_ids:
                    print(f"    -> 이미 저장된 글 '{full_title[:30]}...' 발견. 목록 수집 중단.")
                    stop_crawling = True
                    break
                
                post_data = {
                    "department": DEPARTMENT,
                    "title": full_title,
                    "author": "N/A",
                    "date": date,
                    "link": content_link, # 2단계에서 이 링크(API)를 호출함
                    "custom_id": notice_index
                }
                
                new_posts_metadata.append(post_data)
                
                # 다음 루프를 위해 마지막 인덱스 업데이트
                last_notice_index = notice_index

            time.sleep(0.5)

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
        link = post['link'] # API 주소
        print(f"본문 수집 중 ({i + 1}/{len(posts_metadata)}): {post['title'][:30]}...")
        
        try:
            soup = get_soup(driver, link, delay=0.5)
            
            if soup.find("pre"):
                json_str = soup.find("pre").text
            else:
                json_str = soup.text
            
            data = json.loads(json_str)
            data_modify = data.get('data_modify', {})
            
            if data_modify:
                # HTML 태그가 포함된 본문
                content_html = data_modify.get('Content', '')
                
                # HTML 태그 제거 (BeautifulSoup 활용)
                # content_html이 단순 문자열이므로 다시 BS로 감쌈
                from bs4 import BeautifulSoup 
                content_soup = BeautifulSoup(content_html, "html.parser")
                content_text = content_soup.get_text(separator="\n", strip=True)
                
                # 날짜 정보가 있다면 업데이트 (API 응답 필드 확인 필요, 통상 RegDate)
                if 'RegDate' in data_modify:
                    post['date'] = data_modify['RegDate'].split()[0] # 2025-01-01 12:00:00 -> 2025-01-01
                
                # 첨부파일 확인
                if data_modify.get('OrgFile'):
                    file_name = data_modify['OrgFile']
                    # 다운로드 링크는 소스코드의 modal_notice 함수 참조: /download_file?filename=...
                    # file_path = data_modify.get('FileData')
                    content_text += f"\n\n[첨부파일: {file_name}]"
                
                post['content'] = content_text
                
            else:
                post['content'] = "[본문 데이터가 없습니다 (JSON Empty)]"

        except Exception as e:
            print(f"    [에러] '{post['title']}' 본문 수집 중 오류: {e}")
            post['content'] = f"[수집 오류 발생: {e}]"
            
        time.sleep(0.3) 
        
    print(f"--- [{DEPARTMENT}] 2단계 완료. {len(posts_metadata)}개 본문 수집 완료 ---")
    return posts_metadata