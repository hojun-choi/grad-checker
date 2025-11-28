package kr.ac.dbapp.team1.gradchecker.repo;

import jakarta.persistence.EntityManager;
import jakarta.persistence.TypedQuery;
import jakarta.persistence.criteria.*;
import kr.ac.dbapp.team1.gradchecker.domain.BoardType;
import kr.ac.dbapp.team1.gradchecker.domain.Post;
import kr.ac.dbapp.team1.gradchecker.dto.PostSearchRequest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;

@Repository
@Transactional(readOnly = true)
public class PostRepositoryImpl implements PostRepositoryCustom {

    private final EntityManager em;

    public PostRepositoryImpl(EntityManager em) {
        this.em = em;
    }

    @Override
    public Page<Post> searchPosts(PostSearchRequest searchRequest, Pageable pageable) {
        CriteriaBuilder cb = em.getCriteriaBuilder();

        // SELECT 쿼리
        CriteriaQuery<Post> query = cb.createQuery(Post.class);
        Root<Post> post = query.from(Post.class);

        // Post 테이블과 BoardType 테이블 LEFT JOIN
        Join<Post, BoardType> boardTypeJoin = post.join("boardType", JoinType.LEFT);

        // 검색 조건 동적 생성
        List<Predicate> predicates = getPredicates(searchRequest, cb, post, boardTypeJoin);

        // WHERE
        query.where(predicates.toArray(new Predicate[0]));

        // 정렬
        applySorting(pageable, query, cb, post);

        // 페이징 적용
        TypedQuery<Post> typedQuery = em.createQuery(query);
        typedQuery.setFirstResult((int) pageable.getOffset());
        typedQuery.setMaxResults(pageable.getPageSize());

        List<Post> posts = typedQuery.getResultList();

        // 전체 카운트
        long total = countTotal(searchRequest, cb);

        return new PageImpl<>(posts, pageable, total);
    }

    private List<Predicate> getPredicates(PostSearchRequest searchRequest,
                                          CriteriaBuilder cb,
                                          Root<Post> post,
                                          Join<Post, BoardType> boardTypeJoin) {
        List<Predicate> predicates = new ArrayList<>();

        // 기본 조건: 삭제되지 않은 게시글만
        predicates.add(cb.isFalse(post.get("isDeleted")));

        // 게시판 이름 필터링
        if (searchRequest.getBoardName() != null && !searchRequest.getBoardName().isEmpty()) {
            predicates.add(cb.equal(boardTypeJoin.get("boardName"), searchRequest.getBoardName()));
        }

        // 키워드 검색 (제목 / 내용 / 작성자)
        if (searchRequest.getKeyword() != null && !searchRequest.getKeyword().isEmpty()) {
            String keyword = "%" + searchRequest.getKeyword() + "%";

            if ("title".equalsIgnoreCase(searchRequest.getSearchType())) {
                predicates.add(cb.like(post.get("title"), keyword));
            } else if ("author".equalsIgnoreCase(searchRequest.getSearchType())) {
                // TODO: User 엔티티와 조인 후 username 기준 검색으로 변경 가능
                predicates.add(cb.like(post.get("title"), keyword));
            } else {
                // 기본: 제목 + 내용 OR 검색
                predicates.add(cb.or(
                        cb.like(post.get("title"), keyword),
                        cb.like(post.get("content"), keyword)
                ));
            }
        }

        return predicates;
    }

    // 정렬 로직
    private void applySorting(Pageable pageable,
                              CriteriaQuery<Post> query,
                              CriteriaBuilder cb,
                              Root<Post> post) {
        if (pageable.getSort().isSorted()) {
            List<Order> orders = new ArrayList<>();
            for (Sort.Order sortOrder : pageable.getSort()) {
                if (sortOrder.isAscending()) {
                    orders.add(cb.asc(post.get(sortOrder.getProperty())));
                } else {
                    orders.add(cb.desc(post.get(sortOrder.getProperty())));
                }
            }
            query.orderBy(orders);
        }
    }

    // 전체 카운트 쿼리 (동일 조건 적용)
    private long countTotal(PostSearchRequest searchRequest, CriteriaBuilder cb) {
        CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
        Root<Post> countRoot = countQuery.from(Post.class);
        Join<Post, BoardType> boardTypeJoin = countRoot.join("boardType", JoinType.LEFT);

        List<Predicate> predicates = getPredicates(searchRequest, cb, countRoot, boardTypeJoin);

        countQuery.select(cb.count(countRoot));
        countQuery.where(predicates.toArray(new Predicate[0]));

        return em.createQuery(countQuery).getSingleResult();
    }
}
