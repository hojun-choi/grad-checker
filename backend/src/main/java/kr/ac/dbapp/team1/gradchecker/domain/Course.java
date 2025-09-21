package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
public class Course {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @Column(nullable=false, unique=true)
  private String code;

  @Column(nullable=false)
  private String name;

  private int credits;          // 학점
  @Column(nullable=false)
  private String type;          // MAJOR / GE / FREE
  private String geArea;        // BASIC / CORE / BALANCE ...
}
