// src/main/java/kr/ac/dbapp/team1/gradchecker/web/UserTimetableController.java
package kr.ac.dbapp.team1.gradchecker.web;

import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.dto.TimetableClassDto;
import kr.ac.dbapp.team1.gradchecker.dto.UserTimetableCreateRequest;
import kr.ac.dbapp.team1.gradchecker.dto.UserTimetableDto;
import kr.ac.dbapp.team1.gradchecker.service.UserTimetableService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/user-timetables")
@RequiredArgsConstructor
public class UserTimetableController {

    private final UserTimetableService userTimetableService;
    private final CurrentUserSupport currentUserSupport;

    // GET /api/user-timetables?year=&semester=
    @GetMapping
    public List<UserTimetableDto> getMyTimetables(
            @RequestParam("year") int year,
            @RequestParam("semester") String semester
    ) {
        User user = currentUserSupport.getCurrentUser();
        return userTimetableService.getTimetables(user, year, semester);
    }

    // GET /api/user-timetables/{id}
    @GetMapping("/{id}")
    public UserTimetableDto getTimetableDetail(@PathVariable("id") Long id) {
        User user = currentUserSupport.getCurrentUser();
        return userTimetableService.getTimetableDetail(user, id);
    }

    // POST /api/user-timetables
    @PostMapping
    public UserTimetableDto createTimetable(@RequestBody UserTimetableCreateRequest request) {
        User user = currentUserSupport.getCurrentUser();
        return userTimetableService.createTimetable(user, request);
    }

    // PATCH /api/user-timetables/{id}/primary
    @PatchMapping("/{id}/primary")
    public void setPrimary(@PathVariable("id") Long id) {
        User user = currentUserSupport.getCurrentUser();
        userTimetableService.setPrimary(user, id);
    }

    // POST /api/user-timetables/{id}/courses   (시간표에 수업 넣기)
    @PostMapping("/{id}/courses")
    public TimetableClassDto addCourse(
            @PathVariable("id") Long timetableId,
            @RequestParam("lectureTimetableId") Long lectureTimetableId
    ) {
        User user = currentUserSupport.getCurrentUser();
        return userTimetableService.addCourse(user, timetableId, lectureTimetableId);
    }

    // DELETE /api/user-timetables/{id}/courses/{courseId} (시간표에서 수업 빼기)
    @DeleteMapping("/{id}/courses/{courseId}")
    public void removeCourse(
            @PathVariable("id") Long timetableId,
            @PathVariable("courseId") Long courseId
    ) {
        User user = currentUserSupport.getCurrentUser();
        userTimetableService.removeCourse(user, timetableId, courseId);
    }
}
