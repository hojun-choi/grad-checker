// src/main/java/kr/ac/dbapp/team1/gradchecker/service/PostService.java
package kr.ac.dbapp.team1.gradchecker.service;

import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import kr.ac.dbapp.team1.gradchecker.domain.User;
import kr.ac.dbapp.team1.gradchecker.dto.*;
import kr.ac.dbapp.team1.gradchecker.repo.CommentRepository;
import kr.ac.dbapp.team1.gradchecker.repo.PostRepository;
import kr.ac.dbapp.team1.gradchecker.repo.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.NoSuchElementException;

@Service
@RequiredArgsConstructor
public class PostService {

    private final PostRepository postRepository;
    private final BoardTypeService boardTypeService;
    private final CommentRepository commentRepository;
    private final UserRepository userRepository;

    /**
     * 글 작성
     */
    @Transactional
    public Long createPost(PostRequest request, Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new NoSuchElementException("사용자를 찾을 수 없습니다."));

        BoardType boardType = boardTypeService.getByBoardNameOrThrow(request.getBoardName());

        Post post = Post.builder()
                .user(user)
                .boardType(boardType)
                .title(request.getTitle())
                .content(request.getContent())
                .isAnonymous(request.isAnonymous())
                .commentCount(0)
                .viewCount(0)
                .isDeleted(false)
                .build();

        postRepository.save(post);
        return post.getId();
    }

    /**
     * 글 목록 (검색 + 정렬 + 페이징)
     */
    @Transactional(readOnly = true)
    public Page<PostResponse> searchPosts(PostSearchRequest searchRequest) {

        String sortBy = searchRequest.getSortBy() == null ? "latest" : searchRequest.getSortBy();
        Sort sort;

        if ("popular".equalsIgnoreCase(sortBy)) {
            sort = Sort.by(Sort.Direction.DESC, "viewCount");
        } else {
            sort = Sort.by(Sort.Direction.DESC, "createdAt");
        }

        int page = Math.max(searchRequest.getPage(), 0);
        int size = searchRequest.getSize() > 0 ? searchRequest.getSize() : 20;

        Pageable pageable = PageRequest.of(page, size, sort);

        Page<Post> postPage = postRepository.search(
                searchRequest.getBoardName(),
                searchRequest.getKeyword(),
                pageable
        );

        return postPage.map(PostResponse::from);
    }

    /**
     * 글 단건 조회 (+조회수 증가, 댓글 포함)
     */
    @Transactional
    public PostResponse getPostById(Long postId) {
        Post post = postRepository.findByIdAndIsDeletedFalse(postId)
                .orElseThrow(() -> new NoSuchElementException("게시글을 찾을 수 없습니다."));

        // 조회수 증가
        post.increaseViewCount();

        var comments = commentRepository.findByPostAndIsDeletedFalseOrderByCreatedAtAsc(post)
                .stream()
                .map(CommentResponse::from)
                .toList();

        return PostResponse.from(post, comments);
    }

    /**
     * 글 수정
     */
    @Transactional
    public void updatePost(Long postId, PostRequest request, Long userId) {
        Post post = postRepository.findByIdAndIsDeletedFalse(postId)
                .orElseThrow(() -> new NoSuchElementException("게시글을 찾을 수 없습니다."));

        // 🔐 작성자 본인 확인
        if (!post.getUser().getUserId().equals(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인이 작성한 글만 수정할 수 있습니다.");
        }

        BoardType boardType = boardTypeService.getByBoardNameOrThrow(request.getBoardName());

        post.setBoardType(boardType);
        post.setTitle(request.getTitle());
        post.setContent(request.getContent());
        post.setIsAnonymous(request.isAnonymous());
    }

    /**
     * 글 삭제 (soft delete)
     */
    @Transactional
    public void deletePost(Long postId, Long userId) {
        Post post = postRepository.findByIdAndIsDeletedFalse(postId)
                .orElseThrow(() -> new NoSuchElementException("게시글을 찾을 수 없습니다."));

        // 🔐 작성자 본인 확인
        if (!post.getUser().getUserId().equals(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "본인이 작성한 글만 삭제할 수 있습니다.");
        }

        post.setIsDeleted(true);
    }
}
