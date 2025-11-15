새로 학과 추가하는 과정
1. script/소속대학/학과명.py추가
2. 게시글 목록을 크롤링하는 함수 def get_post_links(driver, old_post_ids, max_pages_to_scan): 
3. 게시글 내용을 크롤링하는 함수 def get_post_contents(driver, posts_metadata):
4. main함수에서 import 및 CRAWLER_CONFIG에 내용 추가.

자세한 내용은 기존 코드 참조
