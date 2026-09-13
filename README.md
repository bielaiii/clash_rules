# Clash 分流配置

这是一个面向 mihomo/Clash Meta 的可维护配置模板：

- 节点订阅地址放在未提交的 `config/subscription.env`，规则地址放在独立的 `config/rules.env`，两者解耦。
- `RULES_BASE_URL` 默认使用知名开源规则仓库；`LOCAL_RULES_BASE_URL` 是可选项，只有你维护自有规则时才填写。
- 自定义白名单、黑名单、直连和代理规则放在 `rules/local/`。
- 远程规则由 `rule-providers` 定时从 GitHub Raw 拉取；`scripts/update_remote_rules.py` 还可以把远程 Git 仓库的规则目录完整镜像到本仓库。
- `scripts/render_config.py` 生成可直接粘贴到 Clash 的 `dist/clash.yaml`。
- GitHub Actions 每天自动检查远程规则仓库，有变化就提交更新；也可以手动运行。

## 第一次使用

1. 复制环境文件并填写订阅地址；需要自有规则时再填写规则地址：

   ```bash
   cp config/subscription.env.example config/subscription.env
   cp config/rules.env.example config/rules.env
   $EDITOR config/subscription.env
   ```

   `SUBSCRIPTION_URL` 是你的机场/节点订阅地址，不会写入 Git。默认的 `RULES_BASE_URL` 已经可以使用；如果要启用自己的白名单、黑名单等，再编辑 `config/rules.env` 中的 `LOCAL_RULES_BASE_URL`。

2. 如果启用了自有规则，设置本仓库发布后的 Raw 地址。若仓库是
   `https://github.com/you/clash_rules`，则填写：

   ```dotenv
   LOCAL_RULES_BASE_URL=https://raw.githubusercontent.com/you/clash_rules/main/rules/local
   ```

   本地规则必须先 push，远程 Clash 才能读到最新内容；不填写该地址时，本地规则提供器不会写入生成的 YAML。

3. 生成配置并检查：

   ```bash
   python3 scripts/render_config.py
   python3 scripts/validate_config.py
   ```

   输出文件为 `dist/clash.yaml`。在 Clash/Mihomo 中导入它即可；之后 Clash 会按 `rule-providers` 的 `interval` 自动更新规则，配置本身则通过你发布的 Raw URL 更新。

## 远程 Git 规则仓库

默认源是 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)，覆盖 Google、Microsoft、Apple、OpenAI、Telegram、YouTube、Steam 和广告规则。要换成自己的规则仓库：

```bash
cp config/remote.env.example config/remote.env
$EDITOR config/remote.env
python3 scripts/update_remote_rules.py
```

`REMOTE_RULE_PATHS` 可以写多个相对目录，逗号分隔；脚本会把这些目录下的全部规则文件同步到 `rules/remote/`，因此远程仓库新增规则文件也会被纳入镜像。规则在线使用时仍由 `RULES_BASE_URL` 直接拉取，能减少本仓库提交大文件；镜像目录主要用于审计、备份和 CI 检查。

若把本仓库放到 GitHub，启用 Actions 后即可每天自动同步：`.github/workflows/update-rules.yml`。首次使用时请在 workflow 的 `env` 中把 `RULES_REPO_URL` 改成你的远程 Git 仓库。

## 分流逻辑

匹配顺序是：本地白名单 → 本地黑名单 → 广告拦截 → 具体应用（OpenAI/Google/Microsoft/Apple/Telegram/YouTube/Steam）→ 中国大陆域名/IP → 常见外国网站 → 国家/地区 IP → 兜底。

配置内置美国、日本、新加坡、香港、台湾地区策略组。应用规则优先于地区规则；例如 OpenAI 命中后会进入 `🤖 OpenAI`，不会被后面的美国 IP 规则抢先匹配。

> 建议使用 mihomo/Clash Meta。传统 Clash 不支持 `GEOSITE`、`rule-providers` 的部分新格式和完整的 `proxy-providers` 能力。

## 直接订阅地址

推荐把 `dist/clash.yaml` 发布到 GitHub Pages、Release 静态文件或其他 HTTPS 静态地址，然后在 Clash 中订阅该地址。订阅地址和规则地址相互独立：节点订阅由 `config/subscription.env` 的 `SUBSCRIPTION_URL` 控制，规则由 `config/rules.env` 的 `RULES_BASE_URL` 与 `LOCAL_RULES_BASE_URL` 控制。

不要把带有个人 token 的 `dist/clash.yaml` 提交到公开仓库；公开发布时使用私有仓库、受保护的静态托管，或在客户端本地生成配置。
