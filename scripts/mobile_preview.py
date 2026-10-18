"""Launch synthetic M1 preview on a private LAN interface, separate from 8501."""

import argparse
from ipaddress import IPv4Address, IPv4Network
import os
from pathlib import Path
import re
import subprocess


PORT = 8502
PRIVATE_NETWORKS = tuple(IPv4Network(net) for net in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))


def private_lan_address(run=subprocess.run):
    """Prefer the active physical interface; do not bind VPN or public addresses."""
    try:
        route = run(["/sbin/route", "-n", "get", "default"], capture_output=True, text=True, check=False)
        match = re.search(r"interface:\s*(en\d+)", route.stdout)
        interfaces = list(dict.fromkeys(([match[1]] if match else []) + ["en0", "en1"]))
        for interface in interfaces:
            output = run(["/usr/sbin/ipconfig", "getifaddr", interface], capture_output=True, text=True, check=False)
            try:
                address = IPv4Address(output.stdout.strip())
            except ValueError:
                continue
            if any(address in network for network in PRIVATE_NETWORKS):
                return str(address)
    except OSError:
        pass
    raise RuntimeError("无法读取可用的内网地址。请将 Mac 连接到与 iPhone 相同的 Wi-Fi，并在本机终端启动手机预览。")


def main():
    parser = argparse.ArgumentParser(description="Stock Copilot 手机预览")
    parser.add_argument("--print-url", action="store_true", help="仅显示地址，不启动服务")
    args = parser.parse_args()
    try:
        address = private_lan_address()
    except RuntimeError as exc:
        print(str(exc), flush=True)
        return 1
    url = f"http://{address}:{PORT}"
    if args.print_url:
        print(url)
        return 0
    root = Path(__file__).resolve().parents[1]
    python = root / ".venv" / "bin" / "python"
    if not python.exists():
        print("请先按 README 安装项目环境。", flush=True)
        return 1
    print(f"\niPhone 与 Mac 连接同一 Wi-Fi，在 Safari 打开：\n\n  {url}\n", flush=True)
    print("仅供可信局域网中的模拟数据预览；不要录入真实信息。", flush=True)
    print("保持 Mac 唤醒、此窗口开启；按 Control+C 停止手机预览。\n", flush=True)
    os.chdir(root)
    os.execv(str(python), [str(python), "-m", "streamlit", "run", "app.py",
                         "--server.address", address, "--server.port", str(PORT),
                         "--browser.serverAddress", address, "--server.headless", "true"])


if __name__ == "__main__":
    raise SystemExit(main())
