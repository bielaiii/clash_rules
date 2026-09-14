/**
 * Clash Verge Rev 全局扩展脚本
 *
 * 请与同目录的 global_override.yaml 一起使用：
 * - global_override.yaml：固定配置、DNS、TUN、规则集和分流规则
 * - 本脚本：根据当前订阅动态生成策略组
 *
 * 订阅地址直接在 Clash Verge Rev 中添加。更新订阅后，本脚本会再次处理
 * 最新配置，新增/删除节点不需要重新运行任何本地脚本。
 */

const GROUP = {
  select: "🚀 节点选择",
  manual: "📶 手动测速",
  foreign: "🌐 常见外国网页",
  openai: "🤖 OpenAI",
  microsoft: "Ⓜ️ Microsoft",
  apple: "🍎 Apple",
  telegram: "📲 Telegram",
  youtube: "📺 YouTube",
  steam: "🎮 Steam",
  china: "🇨🇳 中国大陆",
  fallback: "🐟 漏网之鱼",
  us: "🇺🇸 美国地区",
  jp: "🇯🇵 日本地区",
  sg: "🇸🇬 新加坡地区",
  hk: "🇭🇰 香港地区",
  tw: "🇹🇼 台湾地区",
  blacklist: "🧱 黑名单",
};

function regionGroup(name, filter) {
  return {
    name: name,
    type: "select",
    // 只自动包含当前订阅中符合地区名称的节点，不加入手动测速组。
    "include-all": true,
    filter: filter,
  };
}

function buildProxyGroups() {
  return [
    {
      name: GROUP.select,
      type: "select",
      proxies: [
        GROUP.manual,
        GROUP.us,
        GROUP.jp,
        GROUP.sg,
        GROUP.hk,
        GROUP.tw,
        "DIRECT",
      ],
    },
    {
      // 订阅更新后新增节点会自动出现在这里，保持手动选择，不自动切换。
      name: GROUP.manual,
      type: "select",
      "include-all": true,
    },
    {
      name: GROUP.foreign,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.openai,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.microsoft,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.apple,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.telegram,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.youtube,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.steam,
      type: "select",
      proxies: [GROUP.select, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.china,
      type: "select",
      proxies: ["DIRECT", GROUP.select],
    },
    {
      // 未命中其它规则的流量在这里单独选择出口。
      name: GROUP.fallback,
      type: "select",
      proxies: [
        GROUP.select,
        GROUP.foreign,
        GROUP.us,
        GROUP.jp,
        GROUP.sg,
        GROUP.hk,
        GROUP.tw,
        "DIRECT",
      ],
    },
    regionGroup(GROUP.us, "(?i)美国|US|United States|洛杉矶|纽约|西雅图|硅谷|华盛顿"),
    regionGroup(GROUP.jp, "(?i)日本|JP|Japan|东京|大阪"),
    regionGroup(GROUP.sg, "(?i)新加坡|SG|Singapore"),
    regionGroup(GROUP.hk, "(?i)香港|HK|Hong Kong"),
    regionGroup(GROUP.tw, "(?i)台湾|TW|Taiwan|台北"),
    {
      name: GROUP.blacklist,
      type: "select",
      proxies: ["REJECT", GROUP.select],
    },
  ];
}

function main(config) {
  config = config || {};
  config["proxy-groups"] = buildProxyGroups();
  return config;
}

// 方便在本地用 Node 做语法和行为测试；Clash Verge Rev 中 module 不存在。
if (typeof module !== "undefined" && module.exports) {
  module.exports = { main: main };
}
