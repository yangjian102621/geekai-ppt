#!/bin/bash
# 构建 API 基础镜像（Python + 系统依赖 + pip 依赖）
# 仅在 backend/requirements.txt 或系统依赖变更时执行；可选 push 推送到阿里云
# 用法: ./build-base.sh [push]

cd "$(dirname "$0")"
IMAGE=registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-api-base:latest

docker build -t "$IMAGE" -f dockerfile-api-base ../

if [ "$1" = "push" ]; then
  docker push "$IMAGE"
fi
