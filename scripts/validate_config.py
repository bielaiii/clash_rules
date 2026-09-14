#!/usr/bin/env python3
"""Small dependency-free checks for this repository."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "Google", "Microsoft", "Apple", "OpenAI", "Telegram", "YouTube", "Steam",
    "Advertising", "ChinaMax", "RULE-SET,ChinaMax,🇨🇳 中国大陆",
    "MATCH,🐟 漏网之鱼", "📶 手动测速", "tun:", "auto-route: true",
]


def main() -> int:
    render = ROOT / "scripts" / "render_config.py"
    subprocess.run([sys.executable, str(render), "--allow-placeholder"], check=True)
    config = (ROOT / "dist" / "clash.yaml").read_text(encoding="utf-8")
    missing = [item for item in REQUIRED if item not in config]
    local = [ROOT / "rules" / "local" / name for name in ("whitelist.list", "blacklist.list", "direct.list", "proxy.list")]
    if missing:
        print("缺少配置项：" + ", ".join(missing), file=sys.stderr)
        return 1
    if any(not path.exists() for path in local):
        print("rules/local 下存在缺失文件", file=sys.stderr)
        return 1
    if "type: url-test" in config or "♻️ 自动选择" in config:
        print("配置仍包含自动测速/自动切换节点组", file=sys.stderr)
        return 1
    if "/tree/" in config:
        print("规则提供器仍使用 GitHub 网页地址，必须使用 Raw 地址", file=sys.stderr)
        return 1
    if any(item in config for item in ("geodata-mode:", "geox-url:", "GEOSITE,", "GEOIP,")):
        print("配置仍包含 Geo 数据库依赖", file=sys.stderr)
        return 1
    if config.count("RULE-SET,LocalDirect,DIRECT") != 1 or config.count("RULE-SET,LocalProxy,🚀 节点选择") != 1:
        print("本地直连/代理规则重复或缺失", file=sys.stderr)
        return 1
    print(f"validated {len(config.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
