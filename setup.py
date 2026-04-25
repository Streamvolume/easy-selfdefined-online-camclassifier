#!/usr/bin/env python3
"""
自定义类别识别器 - 环境准备与本地服务器
用法: python setup.py

模型文件通过浏览器内的「保存模型到本地」按钮下载，
本脚本只负责下载 JS 依赖库并启动本地 HTTP 服务器。
"""
import os, sys, time, threading, webbrowser
from urllib.request import urlretrieve, urlopen, Request
from urllib.error import URLError
from http.server import HTTPServer, SimpleHTTPRequestHandler

# ── 锚定脚本所在目录（避免从其他路径运行时相对路径失效）────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def absp(*parts):
    return os.path.join(SCRIPT_DIR, *parts)

# ── JS 依赖库（可从 jsDelivr 正常下载）────────────────────────────────────────
JS_LIBS = [
    (
        "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.10.0/dist/tf.min.js",
        absp("libs", "tf.min.js"),
    ),
    (
        "https://cdn.jsdelivr.net/npm/@tensorflow-models/mobilenet@2.1.1/dist/mobilenet.min.js",
        absp("libs", "mobilenet.min.js"),
    ),
    (
        "https://cdn.jsdelivr.net/npm/@tensorflow-models/knn-classifier@1.2.4/dist/knn-classifier.min.js",
        absp("libs", "knn-classifier.min.js"),
    ),
]

# ── 模型目录（由浏览器保存功能写入，Python 只做检测）──────────────────────────
MODEL_KEYS = ["mobilenet_v2_1.0", "mobilenet_v2_0.5", "mobilenet_v1_1.0"]

PORT = 8765

# ── 工具 ─────────────────────────────────────────────────────────────────────

def sep(char="─", n=54): print(char * n)

def progress_hook(count, block, total):
    if total > 0:
        done  = min(count * block, total)
        ratio = done / total
        bar   = "█" * int(ratio * 24) + "░" * (24 - int(ratio * 24))
        sys.stdout.write(f"\r    [{bar}] {done//1024}KB/{total//1024}KB ")
        sys.stdout.flush()

def is_lib_ready(path):
    return os.path.exists(path) and os.path.getsize(path) > 1024

def is_model_ready(key):
    """检查浏览器是否已保存过该模型（存在 model.json 即视为就绪）"""
    path = absp("models", key, "model.json")
    return os.path.exists(path)

def model_status_line(key):
    if is_model_ready(key):
        size_kb = 0
        model_dir = absp("models", key)
        for f in os.listdir(model_dir):
            try:
                size_kb += os.path.getsize(os.path.join(model_dir, f)) // 1024
            except:
                pass
        return f"✓ 已就绪  (~{size_kb} KB)"
    else:
        return "· 未下载  (在浏览器中点击「保存模型」)"

def download_libs():
    os.makedirs(absp("libs"), exist_ok=True)
    all_ok = True
    for url, dest in JS_LIBS:
        name = os.path.basename(dest)
        if is_lib_ready(dest):
            print(f"  ✓ {name} 已就绪，跳过")
            continue
        print(f"  ▸ 下载 {name} ...")
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            tmp = dest + ".tmp"
            urlretrieve(url, tmp, progress_hook)
            print()
            os.replace(tmp, dest)
            print(f"  ✓ {name} 完成")
        except (URLError, OSError) as e:
            print(f"\n  ✗ 下载失败: {e}")
            all_ok = False
    return all_ok

# ── HTTP 服务器（始终从脚本所在目录提供文件）────────────────────────────────────

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SCRIPT_DIR, **kwargs)

    def log_message(self, fmt, *args):
        # 只打印错误
        if args and str(args[1]) not in ("200", "304"):
            super().log_message(fmt, *args)

def start_server():
    server = HTTPServer(("localhost", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server

# ── 主菜单 ───────────────────────────────────────────────────────────────────

def main():
    sep("═")
    print("  自定义类别识别器 — 本地环境管理")
    print(f"  目录: {SCRIPT_DIR}")
    sep("═")

    while True:
        print()

        # JS 库状态
        libs_ok = all(is_lib_ready(dest) for _, dest in JS_LIBS)
        print(f"JS 依赖库: {'✓ 已就绪' if libs_ok else '· 未下载'}")

        # 模型状态
        print("模型文件（通过浏览器保存）:")
        for key in MODEL_KEYS:
            print(f"  {key:25s}  {model_status_line(key)}")

        print()
        print("操作:")
        print("  [1]  下载 JS 依赖库（支持离线运行）")
        print("  [2]  启动服务器并打开浏览器")
        print("  [q]  退出")
        print()

        choice = input("选择 > ").strip().lower()

        if choice == "q":
            sys.exit(0)

        elif choice == "1":
            sep()
            print("下载 JS 依赖库...")
            ok = download_libs()
            if ok:
                print("\n✓ 全部完成。离线时 JS 库将从本地 libs/ 加载。")
            else:
                print("\n✗ 部分失败，请检查网络后重试。")

        elif choice == "2":
            sep()
            print(f"启动服务器 → http://localhost:{PORT}")
            server = start_server()
            url = f"http://localhost:{PORT}/custom-classifier-v3.html"
            print(f"打开: {url}")
            print()
            print("提示：在浏览器中加载模型后，点击顶栏「保存模型」按钮")
            print("      可将模型权重文件保存到 models/<模型名>/ 目录，")
            print("      下次启动后无需联网即可直接使用。")
            print()
            print("按 Ctrl+C 停止服务器")
            sep()
            webbrowser.open(url)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n停止服务器...")
                server.shutdown()
                sys.exit(0)

        else:
            print("无效输入，请输入 1、2 或 q")

if __name__ == "__main__":
    main()
