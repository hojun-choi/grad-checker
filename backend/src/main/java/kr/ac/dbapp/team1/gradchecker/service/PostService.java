package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.Post;
import kr.ac.dbapp.team1.gradchecker.dto.PostRequest;
import kr.ac.dbapp.team1.gradchecker.dto.PostResponse;
import kr.ac.dbapp.team1.gradchecker.dto.PostSearchRequest;
import kr.ac.dbapp.team1.gradchecker.repo.PostRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;
import java.util.NoSuchElementException;

/**
 * 게시글 관련 비즈니스 로직(조회, 저장, 수정, 삭제, 검색)을 처리하는 서비스입니다.
 */
@Service
public class PostService {

    private final PostRepository postRepository;

    public PostService(PostRepository postRepository) {
        this.postRepository = postRepository;
    }

    //글 작성 api
    @Transactional
    public Long createPost(PostRequest request, Long authenticatedUserId) {
        Post post = Post.builder()
                .userId(authenticatedUserId)
                .boardTypeId(request.getBoardTypeId())
                .title(request.getTitle())
                .content(request.getContent())
                .build();

        Post savedPost = postRepository.save(post);
        return savedPost.getId();
    }

    //글 조회 api
    @Transactional
    public PostResponse getPostById(Long postId) {
        // isDeleted=false인 게시글만 조회
        Post post = postRepository.findById(postId)
                .filter(p -> !p.isDeleted()) // 삭제되지 않은 글만 필터링
                .orElseThrow(() -> new NoSuchElementException("조회할 게시글을 찾을 수 없습니다."));

        // 조회수 증가
        post.incrementViewCount();

        // Entity -> Response DTO
        return PostResponse.from(post);
    }

    // 글 수정 api
    @Transactional
    public void updatePost(Long postId, PostRequest request, Long authenticatedUserId) {
        Post post = postRepository.findByIdAndIsDeletedFalse(postId);

        if (post == null) {
            throw new NoSuchElementException("수정할 게시글을 찾을 수 없습니다.");
        }

        // 작성자 본인인지 확인
        if (!post.getUserId().equals(authenticatedUserId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "게시글을 수정할 권한이 없습니다.");
        }

        // 게시글 내용 업데이트 (Post 엔티티의 update 메서드 사용)
        post.update(request.getTitle(), request.getContent(), request.getBoardTypeId());
    }

    // 글 삭제 api
    @Transactional
    public void deletePost(Long postId, Long authenticatedUserId) {
        Post post = postRepository.findById(postId).orElse(null);

        if (post == null || post.isDeleted()) {
            // 이미 삭제되었거나 존재하지 않는 경우
            return;
        }

        // 작성자 본인인지 확인
        if (!post.getUserId().equals(authenticatedUserId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "게시글을 삭제할 권한이 없습니다.");
        }

        // 논리적 삭제 처리 (markAsDeleted 메서드는 Post 엔티티에 구현되어 있어야 합니다.)
        post.markAsDeleted();
    }

    //메인화면 복합 조회 API 구현
    @Transactional(readOnly = true)
    public Page<PostResponse> searchPosts(PostSearchRequest searchRequest) {
        Pageable pageable = searchRequest.toPageable();

        // Custom Repository 메서드 호출
        Page<Post> postsPage = postRepository.searchPosts(searchRequest, pageable);

        // 엔티티 Page 객체를 Response DTO Page 객체로 변환
        return postsPage.map(PostResponse::from);
    }
}