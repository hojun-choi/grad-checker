package kr.ac.dbapp.team1.gradchecker.global.util;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class SecurityUtil {

    /**
     * SecurityContextHolder에서 현재 인증된 사용자의 ID를 반환합니다.
     * 인증되지 않은 경우(익명 사용자 등) null을 반환합니다.
     */
    public static Long getCurrentUserId() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || authentication.getName() == null || 
            authentication.getName().equals("anonymousUser")) {
            return null;
        }

        try {
            // Authentication의 Name(Subject)에 userId(Long)가 문자열로 들어있다고 가정
            return Long.parseLong(authentication.getName());
        } catch (NumberFormatException e) {
            // 만약 Name이 ID가 아니라 username 등의 문자열이라면 
            // 별도의 UserDetails 구현체를 캐스팅해서 ID를 가져오는 로직으로 변경해야 합니다.
            // 여기서는 안전하게 null 반환
            return null;
        }
    }
    
    // MemberService 등에서 사용하는 메서드 이름 호환성 (필요 시 사용)
    public static Long getCurrentMemberId() {
        return getCurrentUserId();
    }
}