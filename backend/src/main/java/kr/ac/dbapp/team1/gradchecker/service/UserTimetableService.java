// src/main/java/kr/ac/dbapp/team1/gradchecker/service/UserTimetableService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.LectureTimetable;
import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.domain.UserTimetable;
import kr.ac.dbapp.team1.gradchecker.domain.UserTimetableCourse;
import kr.ac.dbapp.team1.gradchecker.dto.TimetableClassDto;
import kr.ac.dbapp.team1.gradchecker.dto.UserTimetableCreateRequest;
import kr.ac.dbapp.team1.gradchecker.dto.UserTimetableDto;
import kr.ac.dbapp.team1.gradchecker.dto.TimetableClassProjection;
import kr.ac.dbapp.team1.gradchecker.repo.LectureTimetableRepository;
import kr.ac.dbapp.team1.gradchecker.repo.UserTimetableCourseRepository;
import kr.ac.dbapp.team1.gradchecker.repo.UserTimetableRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional
public class UserTimetableService {

    private final UserTimetableRepository userTimetableRepository;
    private final UserTimetableCourseRepository userTimetableCourseRepository;
    private final LectureTimetableRepository lectureTimetableRepository;

    /**
     * 특정 학년도/학기의 내 시간표 목록 조회 + 각 시간표 안의 과목들(lecture_schedule 기준)
     */
    @Transactional(readOnly = true)
    public List<UserTimetableDto> getTimetables(User user, int year, String semester) {
        List<UserTimetable> list =
                userTimetableRepository.findByUserAndYearAndSemester(user, year, semester);

        return list.stream()
                .map(tt -> {
                    List<TimetableClassDto> classes =
                            userTimetableCourseRepository.findClassesByTimetableId(tt.getId())
                                    .stream()
                                    .map(TimetableClassDto::fromProjection)
                                    .toList();

                    return UserTimetableDto.fromEntity(tt, classes);
                })
                .toList();
    }

    /**
     * 특정 시간표 상세(헤더 + 과목들) 조회
     */
    @Transactional(readOnly = true)
    public UserTimetableDto getTimetableDetail(User user, Long timetableId) {
        UserTimetable tt = userTimetableRepository.findByIdAndUser(timetableId, user)
                .orElseThrow(() -> new IllegalArgumentException("시간표를 찾을 수 없습니다."));

        List<TimetableClassDto> classes =
                userTimetableCourseRepository.findClassesByTimetableId(tt.getId())
                        .stream()
                        .map(TimetableClassDto::fromProjection)
                        .toList();

        return UserTimetableDto.fromEntity(tt, classes);
    }

    /**
     * 새 시간표 생성 (처음에는 과목이 없으므로 classes는 빈 리스트)
     */
    public UserTimetableDto createTimetable(User user, UserTimetableCreateRequest req) {
        List<UserTimetable> existing =
                userTimetableRepository.findByUserAndYearAndSemester(
                        user, req.getYear(), req.getSemester()
                );

        boolean firstInSemester = existing.isEmpty();

        UserTimetable tt = UserTimetable.builder()
                .user(user)
                .year(req.getYear())
                .semester(req.getSemester())
                .name(req.getName())
                .isMain(firstInSemester)
                .build();

        UserTimetable saved = userTimetableRepository.save(tt);
        return UserTimetableDto.fromEntity(saved, Collections.emptyList());
    }

    /**
     * 대표 시간표 설정
     */
    public void setPrimary(User user, Long timetableId) {
        UserTimetable tt = userTimetableRepository.findByIdAndUser(timetableId, user)
                .orElseThrow(() -> new IllegalArgumentException("시간표를 찾을 수 없습니다."));

        List<UserTimetable> sameSemester =
                userTimetableRepository.findByUserAndYearAndSemester(
                        user, tt.getYear(), tt.getSemester()
                );

        sameSemester.forEach(t -> t.setMain(t.getId().equals(timetableId)));
    }

    /**
     * 시간표에 과목 하나 추가:
     *  - user_timetable_course에 한 줄 INSERT
     *  - lecture_schedule까지 조인해서 TimetableClassDto 한 개 반환
     */
    public TimetableClassDto addCourse(User user, Long timetableId, Long lectureTimetableId) {
        UserTimetable tt = userTimetableRepository.findByIdAndUser(timetableId, user)
                .orElseThrow(() -> new IllegalArgumentException("시간표를 찾을 수 없습니다."));

        LectureTimetable lecture = lectureTimetableRepository.findById(lectureTimetableId)
                .orElseThrow(() -> new IllegalArgumentException("강의를 찾을 수 없습니다."));

        // 매핑 엔티티 저장 (실제 DB INSERT 되는 건 이 한 줄)
        UserTimetableCourse course = UserTimetableCourse.builder()
                .userTimetable(tt)
                .lectureTimetable(lecture)
                .build();

        tt.addCourse(course);
        userTimetableCourseRepository.save(course);

        // 방금 넣은 과목에 대한 시간표 정보를 lecture_schedule에서 다시 조회
        TimetableClassProjection row =
                userTimetableCourseRepository
                        .findClassByTimetableAndLecture(timetableId, lectureTimetableId)
                        .stream()
                        .findFirst()
                        .orElseThrow(() ->
                                new IllegalStateException("추가한 강의의 시간표 정보를 찾을 수 없습니다.")
                        );

        return TimetableClassDto.fromProjection(row);
    }

    /**
     * 시간표에서 과목 삭제
     */
    public void removeCourse(User user, Long timetableId, Long courseId) {
        UserTimetable tt = userTimetableRepository.findByIdAndUser(timetableId, user)
                .orElseThrow(() -> new IllegalArgumentException("시간표를 찾을 수 없습니다."));

        UserTimetableCourse course = userTimetableCourseRepository.findById(courseId)
                .orElseThrow(() -> new IllegalArgumentException("수업을 찾을 수 없습니다."));

        if (!course.getUserTimetable().getId().equals(tt.getId())) {
            throw new IllegalArgumentException("이 시간표에 속한 수업이 아닙니다.");
        }

        tt.removeCourse(course);
        userTimetableCourseRepository.delete(course);
    }
}