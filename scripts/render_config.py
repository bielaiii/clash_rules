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


def normalize_raw_base_url(value: str) -> str:
    """Accept a GitHub tree URL and convert it to the Raw directory URL."""
    value = value.rstrip("/")
    marker = "/tree/"
    if value.startswith("https://github.com/") and marker in value:
        repository, revision_and_path = value.split(marker, 1)
        parts = repository.split("/")
        if len(parts) >= 5:
            owner, repo = parts[3], parts[4]
            revision, separator, path = revision_and_path.partition("/")
            raw = f"https://raw.githubusercontent.com/{owner}/{repo}/{revision}"
            return raw + (f"/{path}" if separator else "")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "dist" / "clash.yaml"))
    parser.add_argument("--allow-placeholder", action="store_true")
    args = parser.parse_args()

    subscription_env = load_env(ROOT / "config" / "subscription.env")
    rules_env = load_env(ROOT / "config" / "rules.env")
    env = {**rules_env, **subscription_env}
    subscription_urls = [
        get_value("SUBSCRIPTION_URL", env),
        get_value("SUBSCRIPTION_URL_2", env),
    ]
    subscription_urls = [
        url for url in subscription_urls
        if url and not url.endswith("your-subscription-url")
    ]
    values = {
        "LOCAL_RULES_BASE_URL": normalize_raw_base_url(get_value("LOCAL_RULES_BASE_URL", env)),
        "RULES_BASE_URL": get_value(
            "RULES_BASE_URL", env,
            "https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash",
        ).rstrip("/"),
        "EXTERNAL_CONTROLLER_SECRET": get_value("EXTERNAL_CONTROLLER_SECRET", env),
    }
    if not subscription_urls:
        if not args.allow_placeholder:
            raise SystemExit("缺少订阅地址：请在 config/subscription.env 中填写 SUBSCRIPTION_URL 和/或 SUBSCRIPTION_URL_2。")
        subscription_urls = ["https://example.com/your-subscription-url"]
    local_enabled = bool(
        values["LOCAL_RULES_BASE_URL"]
        and "your-name/your-repo" not in values["LOCAL_RULES_BASE_URL"]
    )
    if values["LOCAL_RULES_BASE_URL"] and not local_enabled and not args.allow_placeholder:
        raise SystemExit("LOCAL_RULES_BASE_URL 仍是示例地址；请填写真实地址，或删除该配置以关闭自有规则。")

    template = (ROOT / "templates" / "clash.yaml.tmpl").read_text(encoding="utf-8")
    provider_names = []
    provider_blocks = []
    for index, url in enumerate(subscription_urls, start=1):
        name = "subscription" if index == 1 else f"subscription_{index}"
        provider_names.append(name)
        provider_blocks.append(
            f"""  {name}:
    type: http
    url: {yaml_quote(url)}
    interval: 86400
    path: ./cache/proxy-providers/{name}.yaml
    override:
      additional-prefix: '{'大象' if index == 1 else 'eternal'}｜'
    health-check:
      enable: true
      url: http://www.gstatic.com/generate_204
      interval: 300
      lazy: false"""
        )
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
    rendered = rendered.replace("__SUBSCRIPTION_PROVIDERS__", "\n".join(provider_blocks))
    rendered = rendered.replace("__SUBSCRIPTION_PROVIDER_NAMES__", ", ".join(provider_names))
    rendered = rendered.replace("__LOCAL_RULE_PROVIDERS__", local_providers.rstrip())
    rendered = rendered.replace("__LOCAL_RULES__", local_rules.rstrip())
    for key, value in values.items():
        # Base URLs are already surrounded by quotes in the template because
        # they are followed by a path suffix.
        replacement = value if key.endswith("BASE_URL") else yaml_quote(value)
        rendered = rendered.replace(f"__{key}__", replacement)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
