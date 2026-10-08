#!/usr/bin/env python3
"""Generate a Clash Verge Rev override config with local airport providers."""

from __future__ import annotations

import argparse
from pathlib import Path

from render_config import ROOT, get_value, load_env, yaml_quote


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "dist" / "global_override.yaml"))
    args = parser.parse_args()

    env = {
        **load_env(ROOT / "config" / "rules.env"),
        **load_env(ROOT / "config" / "subscription.env"),
    }
    subscriptions = [
        (1, get_value("SUBSCRIPTION_URL", env)),
        (2, get_value("SUBSCRIPTION_URL_2", env)),
    ]
    subscriptions = [
        (index, url)
        for index, url in subscriptions
        if url and not url.endswith("your-subscription-url")
    ]
    if not subscriptions:
        raise SystemExit(
            "缺少订阅地址：请在 config/subscription.env 中填写 SUBSCRIPTION_URL 和/或 SUBSCRIPTION_URL_2。"
        )

    provider_lines = ["proxy-providers:"]
    for index, url in subscriptions:
        name = f"airport{index}"
        provider_lines.extend(
            [
                f"  {name}:",
                "    type: http",
                f"    url: {yaml_quote(url)}",
                "    interval: 86400",
                f"    path: ./cache/proxy-providers/{name}.yaml",
                "    override:",
                f"      additional-prefix: '{'大象' if index == 1 else 'eternal'}｜'",
                "    health-check:",
                "      enable: true",
                "      url: http://www.gstatic.com/generate_204",
                "      interval: 300",
                "      lazy: false",
            ]
        )

    source = ROOT / "optional" / "geoip" / "global_override.yaml"
    content = source.read_text(encoding="utf-8")
    marker = "# __GENERATED_PROXY_PROVIDERS__"
    if content.count(marker) != 1:
        raise SystemExit(f"覆写配置模板中应且仅应有一个标记：{marker}")
    content = content.replace(marker, "\n".join(provider_lines))

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
