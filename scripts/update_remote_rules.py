#!/usr/bin/env python3
"""Mirror all configured rule directories from a remote Git repository."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip().strip("'\"")
    return values


def run(*args: str, cwd: Path | None = None) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()


def main() -> int:
    env = load_env(ROOT / "config" / "remote.env")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        default=os.getenv(
            "RULES_REPO_URL", env.get("RULES_REPO_URL", "https://github.com/blackmatrix7/ios_rule_script.git")
        ),
    )
    parser.add_argument("--ref", default=os.getenv("RULES_REPO_REF", env.get("RULES_REPO_REF", "master")))
    parser.add_argument("--paths", default=os.getenv("REMOTE_RULE_PATHS", env.get("REMOTE_RULE_PATHS", "rule/Clash")))
    parser.add_argument("--output", default=os.getenv("REMOTE_RULES_OUTPUT", env.get("REMOTE_RULES_OUTPUT", "rules/remote")))
    args = parser.parse_args()
    if not args.repo:
        raise SystemExit("缺少远程仓库地址，请填写 config/remote.env 的 RULES_REPO_URL。")

    output = (ROOT / args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="clash-rules-") as temp:
        checkout = Path(temp) / "repo"
        print(f"cloning {args.repo} @ {args.ref}")
        # A partial + sparse checkout keeps this usable for large rule repos;
        # every file below the configured directories is still mirrored.
        run(
            "git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1",
            "--branch", args.ref, args.repo, str(checkout)
        )
        configured_paths = [p.strip() for p in args.paths.split(",") if p.strip()]
        run("git", "sparse-checkout", "set", "--cone", *configured_paths, cwd=checkout)
        run("git", "checkout", "--quiet", args.ref, cwd=checkout)
        commit = run("git", "rev-parse", "HEAD", cwd=checkout)
        repo_name = args.repo.rstrip("/").rsplit("/", 1)[-1].removesuffix(".git")
        destination = output / repo_name
        if destination.exists():
            shutil.rmtree(destination)
        destination.mkdir(parents=True)
        copied = 0
        for configured in configured_paths:
            source = checkout / configured
            if not source.exists():
                raise SystemExit(f"远程仓库不存在目录：{configured}")
            target = destination / configured
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, target, dirs_exist_ok=True)
            copied += sum(1 for p in source.rglob("*") if p.is_file())

        manifest = {
            "repository": args.repo,
            "ref": args.ref,
            "commit": commit,
            "paths": configured_paths,
            "files_copied": copied,
        }
        (output / "index.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"mirrored {copied} files into {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
