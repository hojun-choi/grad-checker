# ---------- Build stage ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package.json ./
RUN npm install --no-audit --no-fund
COPY frontend ./
RUN npm run build

# ---------- Run stage (Nginx) ----------
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/dist ./

# SPA 라우팅 + /api 프록시 (※ proxy_pass 끝에 슬래시 없음!)
RUN printf 'server { \
  listen 80; \
  server_name _; \
  root /usr/share/nginx/html; \
  location / { try_files $uri $uri/ /index.html; } \
  location /api/ { \
    proxy_pass http://backend:8080; \
    proxy_http_version 1.1; \
    proxy_set_header Host $host; \
    proxy_set_header X-Real-IP $remote_addr; \
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
