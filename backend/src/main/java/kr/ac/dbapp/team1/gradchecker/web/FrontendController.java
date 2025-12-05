// src/main/java/kr/ac/dbapp/team1/gradchecker/web/FrontendController.java
package kr.ac.dbapp.team1.gradchecker.web;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class FrontendController {

    @GetMapping({
            "/",              // 메인
            "/login",
            "/register",
            "/schedule",
            "/board",
            "/board/{id}"     // 필요하면 더 추가
    })
    public String forward() {
        // static/index.html 로 포워드
        return "forward:/index.html";
    }
}
