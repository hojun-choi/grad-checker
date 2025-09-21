plugins {
    id("org.springframework.boot") version "3.5.6"
    id("io.spring.dependency-management") version "1.1.7"
    id("java")
}

group = "kr.ac.dbapp.team1"
version = "0.0.1-SNAPSHOT"

java {
    toolchain { languageVersion.set(JavaLanguageVersion.of(17)) }
}

// ⚠️ 여기서 repositories 블록은 제거해야 합니다 (settings에만 둠)

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-data-jpa")
    implementation("org.springframework.boot:spring-boot-starter-validation")

    // Flyway + MySQL (9.x는 mysql 모듈 별도 필요)
    implementation("org.flywaydb:flyway-core:9.22.3")
    implementation("org.flywaydb:flyway-mysql:9.22.3")

    runtimeOnly("com.mysql:mysql-connector-j:8.4.0")

    compileOnly("org.projectlombok:lombok:1.18.34")
    annotationProcessor("org.projectlombok:lombok:1.18.34")

    testImplementation("org.springframework.boot:spring-boot-starter-test")
}

tasks.test { useJUnitPlatform() }
tasks.withType<JavaCompile> { options.encoding = "UTF-8" }
tasks.bootJar { archiveFileName.set("app.jar") }
