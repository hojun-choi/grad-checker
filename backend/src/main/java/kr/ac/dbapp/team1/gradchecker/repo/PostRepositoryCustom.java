package kr.ac.dbapp.team1.gradchecker.repo;
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import kr.ac.dbapp.team1.gradchecker.dto.PostSearchRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

public interface PostRepositoryCustom {
    // 복잡한 메인 화면 조회 API 구현을 위해 필요합니다.
    Page<Post> searchPosts(PostSearchRequest searchRequest, Pageable pageable);
}