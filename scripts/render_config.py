#!/usr/bin/env python3
"""Render a subscription-aware mihomo configuration without third-party deps."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    return values


def get_value(name: str, env: dict[str, str], default: str = "") -> str:
    return os.environ.get(name, env.get(name, default)).strip()


def yaml_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "dist" / "clash.yaml"))
    parser.add_argument("--allow-placeholder", action="store_true")
    args = parser.parse_args()

    subscription_env = load_env(ROOT / "config" / "subscription.env")
    rules_env = load_env(ROOT / "config" / "rules.env")
    env = {**rules_env, **subscription_env}
    values = {
        "SUBSCRIPTION_URL": get_value("SUBSCRIPTION_URL", env),
        "LOCAL_RULES_BASE_URL": get_value("LOCAL_RULES_BASE_URL", env).rstrip("/"),
        "RULES_BASE_URL": get_value(
            "RULES_BASE_URL", env,
            "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash",
        ).rstrip("/"),
        "EXTERNAL_CONTROLLER_SECRET": get_value("EXTERNAL_CONTROLLER_SECRET", env),
    }
    if not values["SUBSCRIPTION_URL"] or values["SUBSCRIPTION_URL"].endswith("your-subscription-url"):
        if not args.allow_placeholder:
            raise SystemExit("缺少 SUBSCRIPTION_URL：请创建 config/subscription.env 并填写订阅地址。")
        values["SUBSCRIPTION_URL"] = "https://example.com/your-subscription-url"
    local_enabled = bool(
        values["LOCAL_RULES_BASE_URL"]
        and "your-name/your-repo" not in values["LOCAL_RULES_BASE_URL"]
    )
    if values["LOCAL_RULES_BASE_URL"] and not local_enabled and not args.allow_placeholder:
        raise SystemExit("LOCAL_RULES_BASE_URL 仍是示例地址；请填写真实地址，或删除该配置以关闭自有规则。")

    template = (ROOT / "templates" / "clash.yaml.tmpl").read_text(encoding="utf-8")
    secret_line = (
        f"secret: {yaml_quote(values['EXTERNAL_CONTROLLER_SECRET'])}"
        if values["EXTERNAL_CONTROLLER_SECRET"] else "# secret is intentionally unset"
    )
    local_providers = ""
    local_rules = ""
    if local_enabled:
        base = values["LOCAL_RULES_BASE_URL"]
        local_providers = f"""  LocalWhitelist:
    type: http
    behavior: classical
    url: '{base}/whitelist.list'
    format: text
    path: ./cache/rules/local-whitelist.list
    interval: 86400
  LocalBlacklist:
    type: http
    behavior: classical
    url: '{base}/blacklist.list'
    format: text
    path: ./cache/rules/local-blacklist.list
    interval: 86400
  LocalDirect:
    type: http
    behavior: classical
    url: '{base}/direct.list'
    format: text
    path: ./cache/rules/local-direct.list
    interval: 86400
  LocalProxy:
    type: http
    behavior: classical
    url: '{base}/proxy.list'
    format: text
    path: ./cache/rules/local-proxy.list
    interval: 86400
"""
        local_rules = """  - RULE-SET,LocalWhitelist,DIRECT
  - RULE-SET,LocalBlacklist,🧱 黑名单
  - RULE-SET,LocalDirect,DIRECT
  - RULE-SET,LocalProxy,🚀 节点选择
"""
    rendered = template.replace("__SECRET_LINE__", secret_line)
    rendered = rendered.replace("__LOCAL_RULE_PROVIDERS__", local_providers.rstrip())
    rendered = rendered.replace("__LOCAL_RULES__", local_rules.rstrip())
    for key, value in values.items():
        # Base URLs are already surrounded by quotes in the template because
        # they are followed by a path suffix; the subscription is not.
        replacement = value if key.endswith("BASE_URL") else yaml_quote(value)
        rendered = rendered.replace(f"__{key}__", replacement)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
