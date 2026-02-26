#!/usr/bin/env python3
"""
后端 API 启动脚本（跨平台版本）
功能：创建虚拟环境、安装依赖、启动服务
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 颜色输出（Windows 可能不支持，所以提供无颜色版本）
USE_COLOR = sys.stdout.isatty() and platform.system() != 'Windows'

def color_print(text, color=''):
    """彩色打印"""
    if USE_COLOR:
        colors = {
            'green': '\033[0;32m',
            'yellow': '\033[1;33m',
            'red': '\033[0;31m',
            'reset': '\033[0m'
        }
        print(f"{colors.get(color, '')}{text}{colors.get('reset', '')}")
    else:
        print(text)

def run_command(cmd, check=True, shell=False):
    """运行命令"""
    try:
        if isinstance(cmd, str):
            cmd = cmd.split()
        result = subprocess.run(cmd, check=check, shell=shell, 
                               capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        color_print(f"错误: {e}", 'red')
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        sys.exit(1)

def main():
    # 获取脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    color_print("=== AI PPT Backend 启动脚本 ===", 'green')
    
    # 检查 Python 版本
    python_version = sys.version
    color_print(f"Python 版本: {python_version}", 'green')
    
    if sys.version_info < (3, 7):
        color_print("错误: 需要 Python 3.7 或更高版本", 'red')
        sys.exit(1)
    
    # 虚拟环境目录
    venv_dir = script_dir / "venv"
    
    # 创建虚拟环境（如果不存在）
    if not venv_dir.exists():
        color_print("创建虚拟环境...", 'yellow')
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
        color_print("虚拟环境创建成功", 'green')
    else:
        color_print("虚拟环境已存在", 'green')
    
    # 确定虚拟环境中的 Python 和 pip
    if platform.system() == 'Windows':
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"
    
    # 升级 pip
    color_print("升级 pip...", 'yellow')
    run_command([str(venv_pip), "install", "--upgrade", "pip", "--quiet"])
    
    # 安装依赖
    color_print("安装依赖包...", 'yellow')
    requirements_file = script_dir / "requirements.txt"
    if requirements_file.exists():
        run_command([str(venv_pip), "install", "-r", str(requirements_file)])
        color_print("依赖安装完成", 'green')
    else:
        color_print("错误: 未找到 requirements.txt", 'red')
        sys.exit(1)
    
    # 检查 .env 文件
    env_file = script_dir / ".env"
    if not env_file.exists():
        color_print("警告: 未找到 .env 文件，将创建默认配置", 'yellow')
        env_content = """API_KEY=
BASE_URL=https://api.geekai.pro
MODEL_LOGIC=google/gemini-3-pro-preview
MODEL_IMAGE=gemini-2.5-pro
PORT=8002
"""
        env_file.write_text(env_content, encoding='utf-8')
        color_print("请编辑 .env 文件设置你的 API_KEY", 'yellow')
    
    # 创建必要的目录
    (script_dir / "storage" / "images").mkdir(parents=True, exist_ok=True)
    (script_dir / "storage" / "sessions").mkdir(parents=True, exist_ok=True)
    
    # 启动服务
    color_print("启动 FastAPI 服务...", 'green')
    color_print("服务将在 http://localhost:8002 运行", 'green')
    color_print("按 Ctrl+C 停止服务", 'yellow')
    print()
    
    # 使用虚拟环境中的 Python 运行 main.py
    os.execv(str(venv_python), [str(venv_python), "main.py"])

if __name__ == "__main__":
    main()
