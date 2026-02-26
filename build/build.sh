#!/bin/bash

version=$1

# 确保在 build 目录中执行（如果从项目根目录运行脚本）
cd "$(dirname "$0")"

# remove docker image if exists
docker rmi -f registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-api:$version
# build docker image for Geek-AI API
docker build -t registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-api:$version -f dockerfile-api ../

# 前端在本地构建，然后复制到 Docker 镜像中（避免在 Docker 内构建，节省时间）
echo "Building frontend locally..."
cd ../web
npm run build || pnpm run build
cd ../build

# build docker image for Geek-AI-web
docker rmi -f registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-web:$version
docker build -t registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-web:$version -f dockerfile-web ../

if [ "$2" = "push" ]; then
  docker push registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-api:$version
  docker push registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-web:$version
fi
