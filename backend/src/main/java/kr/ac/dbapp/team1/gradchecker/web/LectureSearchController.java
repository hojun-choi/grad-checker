// src/main/java/kr/ac/dbapp/team1/gradchecker/web/LectureSearchController.java
package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.dto.LectureDto;
import kr.ac.dbapp.team1.gradchecker.service.LectureSearchService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/lectures")
@RequiredArgsConstructor
public class LectureSearchController {

    private final LectureSearchService lectureSearchService;

    /**
     * 전공 강의
     *  GET /api/lectures/major?year=2025&semester=2학기&ttMajor=기독교
     */
    @GetMapping("/major")
    public List<LectureDto> getMajorLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester,
            @RequestParam("ttMajor") String ttMajor
    ) {
        return lectureSearchService.findMajorLectures(year, semester, ttMajor);
    }

    /**
     * 교양필수(교필)
     *  GET /api/lectures/core?year=2025&semester=2학기
     */
    @GetMapping("/core")
    public List<LectureDto> getCoreLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester
    ) {
        return lectureSearchService.findCoreLectures(year, semester);
    }

    /**
     * 교양선택(교선)
     *  GET /api/lectures/elective?year=2025&semester=2학기&domain=[‘23이후]인간·언어
     *  domain 파라미터는 선택값 (없으면 전체)
     */
    @GetMapping("/elective")
    public List<LectureDto> getElectiveLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester,
            @RequestParam(value = "domain", required = false) String domain
    ) {
        return lectureSearchService.findElectiveLectures(year, semester, domain);
    }

    /**
     * 채플
     *  GET /api/lectures/chapel?year=2025&semester=2학기
     */
    @GetMapping("/chapel")
    public List<LectureDto> getChapelLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester
    ) {
        return lectureSearchService.findChapelLectures(year, semester);
    }

    /**
     * 교직 (교직, 교직전공)
     *  GET /api/lectures/teaching?year=2025&semester=2학기
     */
    @GetMapping("/teaching")
    public List<LectureDto> getTeachingLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester
    ) {
        return lectureSearchService.findTeachingLectures(year, semester);
    }

    /**
     * 연계전공
     *  GET /api/lectures/linked-major?year=2025&semester=2학기&ttMajor=연계전공이름
     */
    @GetMapping("/linked-major")
    public List<LectureDto> getLinkedMajorLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester,
            @RequestParam("ttMajor") String ttMajor
    ) {
        return lectureSearchService.findLinkedMajorLectures(year, semester, ttMajor);
    }

    /**
     * 융합전공
     *  GET /api/lectures/convergence-major?year=2025&semester=2학기&ttMajor=융합전공이름
     */
    @GetMapping("/convergence-major")
    public List<LectureDto> getConvergenceMajorLectures(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester,
            @RequestParam("ttMajor") String ttMajor
    ) {
        return lectureSearchService.findConvergenceMajorLectures(year, semester, ttMajor);
    }
}
