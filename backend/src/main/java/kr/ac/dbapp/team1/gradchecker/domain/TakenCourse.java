package kr.ac.dbapp.team1.gradchecker.domain;

import jakarta.persistence.*;
import lombok.*;

@Entity @Getter @Setter @NoArgsConstructor @AllArgsConstructor @Builder
@Table(uniqueConstraints = @UniqueConstraint(columnNames = {"student_id","courseCode","term"}))
public class TakenCourse {
  @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne(optional=false)
  private Student student;

  @Column(nullable=false)
  private String courseCode;

  @Column(nullable=false)
  private String grade; // A+, A, B+ ... or P/F

  @Column(nullable=false)
  private String term; // 2024-1
}
