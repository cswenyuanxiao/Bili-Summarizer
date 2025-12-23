import subprocess
import sys
import time
import os

def start_share():
    print("🚀 正在启动本地服务 (测试模式)...")
    
    # 1. 启动本地 FastAPI 服务 (测试模式)
    # 我们使用 8001 端口，配合之前创建的 main_test.py
    cmd = [sys.executable, "-m", "uvicorn", "web_app.main:app", "--host", "127.0.0.1", "--port", "8001"]
    
    try:
        process = subprocess.Popen(cmd)
        
        print("\n" + "="*50)
        print("✅ 本地服务已启动！")
        print("现在请按以下步骤操作来获得【外网分享链接】：")
        print("="*50)
        print("1. 如果没安装 ngrok，请运行: brew install --cask ngrok")
        print("2. 在新窗口运行命令: ngrok http 8001")
        print("3. 复制 ngrok 提供的 https://xxxx.ngrok-free.app 链接发给朋友")
        print("="*50)
        print("💡 为什么这样做？")
        print("这样朋友虽然在远程访问，但下载任务是在你本地 IP 运行的，能避开 B站封锁。")
        print("="*50)
        print("\n按 Ctrl+C 停止分享...")
        
        process.wait()
    except KeyboardInterrupt:
        print("\n👋 正在停止服务...")
        process.terminate()

if __name__ == "__main__":
    start_share()
