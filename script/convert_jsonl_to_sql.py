import json
import os

# 입력 파일명과 출력 파일명 설정
INPUT_FILE = './backend/src/main/resources/data/timetable_transformed.jsonl'
OUTPUT_FILE = './backend/src/main/resources/data_lectures.sql'

def parse_term_code(term_code):
    """
    "20-1" -> (2020, "1학기")
    "21-여름학기" -> (2021, "여름학기")
    형식으로 변환
    """
    if not term_code or '-' not in term_code:
        return 2000, "기타"
    
    year_str, sem_code = term_code.split('-')
    year = 2000 + int(year_str)
    
    semester_map = {
        '1': '1학기',
        '2': '2학기',
        '여름학기': '여름학기',
        '겨울학기': '겨울학기'
    }
    semester = semester_map.get(sem_code, sem_code)
    
    return year, semester

def escape_sql(value):
    """
    SQL 문법에 맞게 문자열 이스케이프 처리
    None -> NULL
    String -> 'String' (작은따옴표 처리 포함)
    Number -> Number
    """
    if value is None:
        return "NULL"
    if isinstance(value, str):
        # 빈 문자열은 그대로 빈 문자열로
        # 작은따옴표(')가 있으면 ('')로 변경 (SQL 표준 이스케이프)
        escaped_value = value.replace("'", "''")
        return f"'{escaped_value}'"
    return str(value)

def main():
    # 경로 확인 (디버깅용)
    print(f"Current working directory: {os.getcwd()}")
    
    if not os.path.exists(INPUT_FILE):
        print(f"오류: '{INPUT_FILE}' 파일이 없습니다.")
        return

    print(f"변환 시작: {INPUT_FILE} -> {OUTPUT_FILE}")
    
    # 출력 파일의 디렉토리가 없으면 생성
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        
        outfile.write("-- 자동 생성된 강의 데이터 SQL\n")
        outfile.write("-- timetableId를 id로 그대로 사용하여 관계를 맺습니다.\n\n")

        count = 0
        for line in infile:
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                count += 1
                
                # -------------------------------------------------------
                # 1. lecture_timetable (메인 테이블) 데이터 준비
                # -------------------------------------------------------
                timetable_id = data.get('timetableId')
                term_code = data.get('termCode')
                year, semester = parse_term_code(term_code)
                
                credit = data.get('credit', {})
                
                # SQL 작성 (INSERT IGNORE 사용)
                # timetableId를 id 컬럼에 직접 넣습니다.
                sql_timetable = (
                    f"INSERT IGNORE INTO lecture_timetable "
                    f"(id, timetable_id, year, semester, course_code, course_title, section_no, "
                    f"instructor_name, department_name, engineering_certification, class_type_info, "
                    f"taking_note, target_students, capacity, enrolled_count, "
                    f"lecture_hours, course_credits, design_credits) "
                    f"VALUES ("
                    f"{timetable_id}, "                 # id (PK로 사용)
                    f"{timetable_id}, "                 # timetable_id (보존용)
                    f"{year}, "                         # year
                    f"'{semester}', "                   # semester
                    f"{escape_sql(data.get('courseCode'))}, "
                    f"{escape_sql(data.get('courseTitle'))}, "
                    f"{escape_sql(data.get('sectionNo'))}, "
                    f"{escape_sql(data.get('instructorName'))}, "
                    f"{escape_sql(data.get('departmentName'))}, "
                    f"{escape_sql(data.get('engineeringCertification'))}, "
                    f"{escape_sql(data.get('classTypeInfo'))}, "
                    f"{escape_sql(data.get('takingNote'))}, "
                    f"{escape_sql(data.get('targetStudents'))}, "
                    f"{data.get('capacity', 0)}, "
                    f"{data.get('enrolledCount', 0)}, "
                    f"{credit.get('lectureHours', 0)}, "
                    f"{credit.get('courseCredits', 0)}, "
                    f"{credit.get('designCredits', 0)}"
                    f");\n"
                )
                outfile.write(sql_timetable)

                # -------------------------------------------------------
                # 2. lecture_schedule (시간표) 데이터 준비
                # -------------------------------------------------------
                meetings = data.get('meetings', [])
                for meeting in meetings:
                    # [수정됨] meeting_id 제외 (AUTO_INCREMENT 사용)
                    sql_schedule = (
                        f"INSERT IGNORE INTO lecture_schedule "
                        f"(lecture_id, meeting_day, start_time, end_time, building_room) "
                        f"VALUES ("
                        f"{timetable_id}, "  # 부모 ID (FK)
                        f"{escape_sql(meeting.get('meetingDay'))}, "
                        f"{escape_sql(meeting.get('startTime'))}, "
                        f"{escape_sql(meeting.get('endTime'))}, "
                        f"{escape_sql(meeting.get('buildingRoom'))}"
                        f");\n"
                    )
                    outfile.write(sql_schedule)

                # -------------------------------------------------------
                # 3. lecture_eligibility (인정 학과) 데이터 준비
                # -------------------------------------------------------
                eligibilities = data.get('eligibilities', [])
                for elig in eligibilities:
                    # [수정됨] eligibility_id 제외 (AUTO_INCREMENT 사용)
                    sql_eligibility = (
                        f"INSERT IGNORE INTO lecture_eligibility "
                        f"(lecture_id, department_name, category_type) "
                        f"VALUES ("
                        f"{timetable_id}, "  # 부모 ID (FK)
                        f"{escape_sql(elig.get('departmentName'))}, "
                        f"{escape_sql(elig.get('categoryType'))}"
                        f");\n"
                    )
                    outfile.write(sql_eligibility)
                
                outfile.write("\n") # 가독성을 위해 줄바꿈

            except json.JSONDecodeError:
                print(f"JSON 파싱 에러 발생 (라인 무시됨): {line[:50]}...")
            except Exception as e:
                print(f"데이터 처리 중 에러 발생: {e}")

    print(f"완료! 총 {count}개의 강의 데이터가 '{OUTPUT_FILE}'에 저장되었습니다.")

if __name__ == "__main__":
    main()