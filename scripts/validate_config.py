#!/usr/bin/env python3
"""Small dependency-free checks for this repository."""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "Google", "Microsoft", "Apple", "OpenAI", "Telegram", "YouTube", "Steam",
    "Advertising", "ChinaMax", "RULE-SET,ChinaMax,🇨🇳 中国大陆",
    "MATCH,🐟 漏网之鱼", "📶 手动测速", "🤖 AI", "tun:", "auto-route: true",
]

GEMINI_RULES = [
    "DOMAIN-SUFFIX,ai.google,Google",
    "DOMAIN-SUFFIX,google.ai,Google",
    "DOMAIN-SUFFIX,gemini.google.com,Google",
    "DOMAIN-SUFFIX,gemini.gstatic.com,Google",
    "DOMAIN,geminiweb-pa.clients6.google.com,Google",
    "DOMAIN,geminiweb-pa.clients.google.com,Google",
    "DOMAIN,geminiweb-pa.googleapis.com,Google",
    "DOMAIN-SUFFIX,aistudio.google.com,Google",
    "DOMAIN-SUFFIX,ai.google.dev,Google",
    "DOMAIN-SUFFIX,generativelanguage.googleapis.com,Google",
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
    for path in (ROOT / "dist" / "clash.yaml", ROOT / "optional" / "geoip" / "global_override.yaml"):
        rules = path.read_text(encoding="utf-8").splitlines()
        google_rule = "  - RULE-SET,Google,Google"
        openai_rule = "  - RULE-SET,OpenAI,🤖 AI"
        ai_rules = [f"  - {rule}" for rule in GEMINI_RULES]
        youtube_rule = "  - RULE-SET,YouTube,📺 YouTube"
        if (
            rules.count(google_rule) != 1
            or rules.count(openai_rule) != 1
            or rules.count(youtube_rule) != 1
            or rules.index(youtube_rule) > rules.index(google_rule)
            or any(rules.count(rule) != 1 or rules.index(rule) > rules.index(google_rule) for rule in ai_rules)
        ):
            print(f"{path}: Google AI/Gemini/OpenAI 分流规则缺失或顺序错误", file=sys.stderr)
            return 1
    if any(not path.exists() for path in local):
        print("rules/local 下存在缺失文件", file=sys.stderr)
        return 1
    if "/tree/" in config:
        print("规则提供器仍使用 GitHub 网页地址，必须使用 Raw 地址", file=sys.stderr)
        return 1
    if any(item in config for item in ("geodata-mode:", "geox-url:", "GEOSITE,", "GEOIP,")):
        print("配置仍包含 Geo 数据库依赖", file=sys.stderr)
        return 1
    local_providers = [
        f"  {name}:" in config
        for name in ("LocalWhitelist", "LocalBlacklist", "LocalDirect", "LocalProxy")
    ]
    local_rules = [
        config.count("RULE-SET,LocalDirect,DIRECT"),
        config.count("RULE-SET,LocalProxy,🚀 节点选择"),
    ]
    if any(local_providers) and not all(local_providers):
        print("本地规则提供器配置不完整", file=sys.stderr)
        return 1
    if (all(local_providers) and local_rules != [1, 1]) or (not any(local_providers) and any(local_rules)):
        print("本地直连/代理规则与提供器配置不一致", file=sys.stderr)
        return 1
    print(f"validated {len(config.splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
