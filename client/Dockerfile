# client/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# 패키지 설치
COPY package*.json ./
RUN npm ci

# 빌드
COPY . .
RUN npm run build

# Nginx 서빙
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
