# Clash 分流全局扩展脚本

这是给 mihomo / Clash Meta 使用的 Clash Verge Rev 全局扩展配置和全局扩展脚本。订阅地址由 Clash Verge Rev 自己管理，两个文件只负责在订阅配置上叠加基础设置、DNS、TUN、策略组和分流规则。

这样设置一次即可：以后点击 Clash Verge Rev 的“更新订阅”时，新节点会自动进入 `📶 手动测速`，不需要重新运行本仓库的 Python 脚本，也不需要重新生成完整 YAML。

## 使用方法：添加两个文件

1. 在 Clash Verge Rev 中正常添加并启用你的机场订阅。
2. 打开 Clash Verge Rev 的“设置 → 覆写/扩展配置”，新建或导入 [`global_override.yaml`](./global_override.yaml)。
3. 再打开“设置 → 覆写/扩展脚本 → 全局扩展脚本”，导入 [`global_script.js`](./global_script.js)。
4. 保存并重新应用订阅。之后只需更新原来的订阅即可。

两个文件都可以直接复制粘贴；如果仓库已发布，也可以分别使用 Raw 地址：

```text
https://raw.githubusercontent.com/bielaiii/clash_rules/main/global_override.yaml
https://raw.githubusercontent.com/bielaiii/clash_rules/main/global_script.js
```

全局扩展配置负责固定字段和规则集；全局扩展脚本的入口是 `main(config, profileName)`，负责使用 `include-all` 和地区过滤器从当前订阅动态构造节点组。具体入口和执行顺序见 [Clash Verge Rev 扩展文档](https://www.clashverge.dev/guide/extend.html) 与 [自定义脚本文档](https://www.clashverge.dev/guide/script.html)。

默认配置不依赖 Geo 数据库。如果需要 GeoIP/GeoSite 分流，使用 [`optional/geoip/global_override.yaml`](./optional/geoip/global_override.yaml) 替换根目录的 `global_override.yaml`，继续使用根目录的 `global_script.js`；不要同时启用两个覆写配置。GeoIP 版会由 mihomo 根据 `geox-url` 下载完整 Geo 数据库，并按配置自动更新。[mihomo GEO 配置说明](https://wiki.metacubex.one/en/config/general/)

## 脚本里的可调项

如果使用本仓库默认规则，两个文件无需修改。若需要调整自有规则地址，编辑 [`global_override.yaml`](./global_override.yaml) 中 `LocalWhitelist`、`LocalBlacklist`、`LocalDirect` 和 `LocalProxy` 的 URL。

远程规则默认使用 blackmatrix7；如果需要换规则源，请在 [`global_override.yaml`](./global_override.yaml) 中批量替换 `https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash`。

当前自有规则地址默认是：

```text
https://raw.githubusercontent.com/bielaiii/clash_rules/main/rules/local
```

如果你修改了 `rules/local/`，需要先 push 到该 Raw 地址对应的仓库；Clash 会按 86400 秒间隔更新规则集。订阅节点本身仍由 Clash Verge Rev 的订阅更新机制负责。

## 分流逻辑

匹配顺序为：本地白名单 → 本地黑名单 → 本地直连/代理 → 广告拦截 → 指定外国网站 → OpenAI → Google → Microsoft → Apple → Telegram → YouTube → Steam → 中国大陆规则集 → `🐟 漏网之鱼`。

Patreon、Discord、Pixiv、WNACG、MediaFire 和 MissKon 已加入 `🌐 常见外国网页`。未命中的流量进入 `🐟 漏网之鱼`，可在那里选择节点总组、常见外国网页、地区组或 `DIRECT`。节点组是手动选择，不会因为测速结果自动切换当前选择。

启用 TUN 后，WSL 和不读取系统代理的软件也可以被 mihomo 接管。Clash Verge Rev 可能要求管理员权限；如果 TUN 不可用，可以参考 [`scripts/wsl-proxy.sh`](./scripts/wsl-proxy.sh) 做备用排查。

## 本地检查

```bash
make test-extension
```

仓库仍保留 [`scripts/render_config.py`](./scripts/render_config.py) 和 `templates/clash.yaml.tmpl`，它们用于需要独立完整 YAML 的场景；日常使用全局扩展脚本时不需要运行它们。

## 远程规则镜像

如果需要把远程 Git 规则仓库镜像到本地审计或备份：

```bash
cp config/remote.env.example config/remote.env
python3 scripts/update_remote_rules.py
```

规则在线使用仍由 `RULES_BASE_URL` 直接拉取；`rules/remote/` 只是镜像目录。
