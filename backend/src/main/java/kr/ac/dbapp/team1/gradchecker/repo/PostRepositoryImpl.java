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

        //SELECT 쿼리
        CriteriaQuery<Post> query = cb.createQuery(Post.class);
        //기본 테이블 Post로 설정
        Root<Post> post = query.from(Post.class);

        //Post테이블과 BoardType 테이블 left join
        Join<Post, BoardType> boardTypeJoin = post.join("boardTypeId", JoinType.LEFT); // 실제로는 엔티티 매핑에 따라 다름

        //검색 조건 만족 시만 쿼리에 조건 추가
        List<Predicate> predicates = getPredicates(searchRequest, cb, post, boardTypeJoin);

        //Where
        query.where(predicates.toArray(new Predicate[0]));

        //최신순, 조회순 쿼리에 추가
        applySorting(pageable, query, cb, post);

        //쿼리 객체 생성
        TypedQuery<Post> typedQuery = em.createQuery(query);
        //페이지네이션 시작점
        typedQuery.setFirstResult((int) pageable.getOffset());
        //페이지네이션 개수
        typedQuery.setMaxResults(pageable.getPageSize());

        //쿼리 실행
        List<Post> posts = typedQuery.getResultList();

        //전체 카운트 조회 (페이지네이션을 위해 필요)
        long total = countTotal(searchRequest, cb, em);

        //조회된 데이터, 페이지 정보, 전체 개수를 Page 객체로 포장 후 서비스로 반환
        return new PageImpl<>(posts, pageable, total);
    }


    private List<Predicate> getPredicates(PostSearchRequest searchRequest, CriteriaBuilder cb, Root<Post> post, Join<Post, BoardType> boardTypeJoin) {
        List<Predicate> predicates = new ArrayList<>();

        //기본 조건
        predicates.add(cb.isFalse(post.get("isDeleted")));

        //게시판 이름 필터링
        if (searchRequest.getBoardName() != null && !searchRequest.getBoardName().isEmpty()) {
            predicates.add(cb.equal(boardTypeJoin.get("board_name"), searchRequest.getBoardName()));
        }

        // 키워드 검색 (제목 또는 작성자 검색)
        if (searchRequest.getKeyword() != null && !searchRequest.getKeyword().isEmpty()) {
            String keyword = "%" + searchRequest.getKeyword() + "%";

            if ("title".equalsIgnoreCase(searchRequest.getSearchType())) {
                predicates.add(cb.like(post.get("title"), keyword));
            } else if ("author".equalsIgnoreCase(searchRequest.getSearchType())) {
                // 작성자 ID(userId)를 기반으로 검색해야 하지만, 여기서는 임시로 title에 대한 검색으로 처리합니다.
                // 실제 구현 시 User 엔티티와 조인하여 username으로 검색해야 합니다.
                predicates.add(cb.like(post.get("title"), keyword));
            } else {
                predicates.add(cb.or(
                        cb.like(post.get("title"), keyword),
                        cb.like(post.get("content"), keyword)
                ));
            }
        }
        return predicates;
    }

    // 정렬 로직
    private void applySorting(Pageable pageable, CriteriaQuery<Post> query, CriteriaBuilder cb, Root<Post> post) {
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

    // 전체 카운트 쿼리
    private long countTotal(PostSearchRequest searchRequest, CriteriaBuilder cb, EntityManager em) {
        CriteriaQuery<Long> countQuery = cb.createQuery(Long.class);
        Root<Post> countRoot = countQuery.from(Post.class);
        countQuery.select(cb.count(countRoot));

        return em.createQuery(countQuery).getSingleResult();
    }
}