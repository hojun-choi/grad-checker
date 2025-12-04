// src/main/java/kr/ac/dbapp/team1/gradchecker/service/LectureSearchService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.dto.LectureDto;
import kr.ac.dbapp.team1.gradchecker.repo.LectureTimetableRepository;
import kr.ac.dbapp.team1.gradchecker.repo.projection.LectureSearchProjection;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class LectureSearchService {

    private final LectureTimetableRepository lectureTimetableRepository;

    /**
     * 전공 강의 검색
     *  - year, semester, ttMajor(예: '기독교') 기준
     *  - major_history는 쿼리에서 year=lt.year AND mh.tt_major=:ttMajor 로 조인
     */
    public List<LectureDto> findMajorLectures(int year, String semester, String ttMajor) {
        List<LectureSearchProjection> list =
                lectureTimetableRepository.findMajorLectures(year, semester, ttMajor);
        return list.stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 교양필수(교필) */
    public List<LectureDto> findCoreLectures(int year, String semester) {
        return lectureTimetableRepository.findCoreLectures(year, semester).stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 교양선택(교선) + domain 필터 */
    public List<LectureDto> findElectiveLectures(int year, String semester, String domain) {
        String domainParam = (domain == null || domain.isBlank()) ? null : domain;
        return lectureTimetableRepository.findElectiveLectures(year, semester, domainParam)
                .stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 채플 */
    public List<LectureDto> findChapelLectures(int year, String semester) {
        return lectureTimetableRepository.findChapelLectures(year, semester).stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 교직 (교직/교직전공) */
    public List<LectureDto> findTeachingLectures(int year, String semester) {
        return lectureTimetableRepository.findTeachingLectures(year, semester).stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 연계전공 (연계1/연계2/연선) */
    public List<LectureDto> findLinkedMajorLectures(int year, String semester, String ttMajor) {
        return lectureTimetableRepository.findLinkedMajorLectures(year, semester, ttMajor).stream()
                .map(LectureDto::fromProjection)
                .toList();
    }

    /** 융합전공 (융필/융선) */
    public List<LectureDto> findConvergenceMajorLectures(int year, String semester, String ttMajor) {
        return lectureTimetableRepository.findConvergenceMajorLectures(year, semester, ttMajor).stream()
                .map(LectureDto::fromProjection)
                .toList();
    }
}
