# Clash 分流全局扩展脚本

这是给 mihomo / Clash Meta 使用的 Clash Verge Rev 全局扩展配置和全局扩展脚本。机场地址保存在本机 `config/subscription.env`，由脚本生成覆写 YAML；机场节点和策略组仍通过 Clash Verge Rev 的扩展配置与扩展脚本加载。

覆写配置引用两个机场 provider，节点分别加上“大象”和“eternal”来源前缀。扩展脚本会把两个机场的全部节点加入各分流组；地区组从两个机场取节点后按地区筛选。

## 使用方法：添加两个文件

1. 在 `config/subscription.env` 中填写 `SUBSCRIPTION_URL` 和 `SUBSCRIPTION_URL_2`。
2. 运行 `make render-override`，生成本地的 `dist/global_override.yaml`。
3. 将生成文件的全部内容粘贴到 Clash Verge Rev 的“设置 → 覆写/扩展配置”。
4. 将 [`global_script.js`](./global_script.js) 的全部内容粘贴到“设置 → 覆写/扩展脚本 → 全局扩展脚本”，保存并重新应用配置。

`dist/global_override.yaml` 包含机场订阅链接，已加入 Git 忽略规则，不要提交或公开分享。修改 `.env` 中的链接后，重新运行 `make render-override`，再更新覆写配置内容。

全局扩展配置负责固定字段、两个机场 provider、DNS、TUN 和分流规则；全局扩展脚本的入口是 `main(config, profileName)`，负责按 provider 动态构造机场组和地区组。具体入口和执行顺序见 [Clash Verge Rev 扩展文档](https://www.clashverge.dev/guide/extend.html) 与 [自定义脚本文档](https://www.clashverge.dev/guide/script.html)。

覆写配置模板位于 [`optional/geoip/global_override.yaml`](./optional/geoip/global_override.yaml)，生成后的覆写文件由 mihomo 根据 `geox-url` 下载并更新 GEO 数据库。[mihomo GEO 配置说明](https://wiki.metacubex.one/en/config/general/)

## 脚本里的可调项

如果使用本仓库默认规则，两个文件无需修改。若需要调整自有规则地址，编辑 [`global_override.yaml`](./global_override.yaml) 中 `LocalWhitelist`、`LocalBlacklist`、`LocalDirect` 和 `LocalProxy` 的 URL。

远程规则默认使用 blackmatrix7；如果需要换规则源，请在 [`global_override.yaml`](./global_override.yaml) 中批量替换 `https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Clash`。

当前自有规则地址默认是：

```text
https://raw.githubusercontent.com/bielaiii/clash_rules/main/rules/local
```

如果你修改了 `rules/local/`，需要先 push 到该 Raw 地址对应的仓库；Clash 会按 86400 秒间隔更新规则集。订阅节点本身仍由 Clash Verge Rev 的订阅更新机制负责。

## 分流逻辑

匹配顺序为：本地白名单 → 本地黑名单 → 本地直连/代理 → 广告拦截 → 指定外国网站（含 `网站分流`）→ OpenAI → Google → Microsoft → Apple → Telegram → YouTube → Steam → 中国大陆规则集 → `🐟 漏网之鱼`。

Patreon、Discord、Pixiv、Docker、MediaFire 和 MissKon 已加入 `🌐 常见外国网页`，Docker 包括网站、认证、镜像仓库及规则源列出的 CDN 域名。特定域名由 `网站分流` 组控制。各分流组可选择对应地区组；日本、新加坡、香港、台湾地区组每 5 分钟后台测速并自动切换到延迟最低的节点，美国地区组保留手动选择。`📶 手动测速` 保留手动选择所有节点的能力。机场 provider 每 5 分钟执行健康检查，关闭懒测速，避免长时间闲置后才触发检查。

DNS 将节点域名和直连请求交给国内 DoH，其他域名使用通过 `🚀 节点选择` 连接的境外 DoH。GeoSite 覆写配置还为国内和私有域名指定国内解析。单独配置 `proxy-server-nameserver` 避免解析节点时依赖代理自身，见 [mihomo DNS 配置](https://wiki.metacubex.one/config/dns/)。TUN 开启 HTTP、TLS 和 QUIC 域名嗅探，以补充浏览器自行解析 DNS 时的域名分流；嗅探不覆盖实际连接地址。

遇到“首次打开失败、刷新正常”时，更新本仓库后运行 `make render-override`，重新粘贴 `dist/global_override.yaml` 和 `global_script.js`，重新应用配置并重启内核。如果使用完整配置，则运行 `make render` 后重新导入 `dist/clash.yaml`。若仍失败，记录首次请求的浏览器错误和 Clash 日志中的匹配规则、实际节点，以区分 DNS、节点连接和 QUIC 问题；后台健康检查不会替手动选择组自动更换节点。

启用 TUN 后，WSL 和不读取系统代理的软件也可以被 mihomo 接管。Clash Verge Rev 可能要求管理员权限；如果 TUN 不可用，可以参考 [`scripts/wsl-proxy.sh`](./scripts/wsl-proxy.sh) 做备用排查。

## 本地生成和检查

```bash
make render-override
make test-extension
```

仓库另保留 [`scripts/render_config.py`](./scripts/render_config.py) 和 `templates/clash.yaml.tmpl`，用于需要独立完整 YAML 的场景；两文件扩展方式使用 `make render-override`。

`config/subscription.env` 已被 Git 忽略，不会提交订阅链接。覆写脚本只输出本地扩展配置，不生成完整配置文件。

## 远程规则镜像

如果需要把远程 Git 规则仓库镜像到本地审计或备份：

```bash
cp config/remote.env.example config/remote.env
python3 scripts/update_remote_rules.py
```

规则在线使用仍由 `RULES_BASE_URL` 直接拉取；`rules/remote/` 只是镜像目录。
