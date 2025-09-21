# backend/Dockerfile
FROM gradle:8.9.0-jdk17 AS builder
WORKDIR /app
COPY backend/ /app/
RUN gradle --no-daemon clean bootJar

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
ENV TZ=Asia/Seoul
COPY --from=builder /app/build/libs/app.jar /app/app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
