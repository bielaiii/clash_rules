/**
 * Clash Verge Rev 全局扩展脚本
 *
 * 请与同目录的 global_override.yaml 一起使用：
 * - global_override.yaml：固定配置、DNS、TUN、规则集和分流规则
 * - 本脚本：根据覆写配置中的 proxy-providers 动态生成机场和节点策略组
 *
 * 机场订阅地址由 scripts/render_override.py 从本地 env 写入覆写配置；
 * mihomo 按 provider 更新节点，本脚本据此生成可单独选择的机场组。
 */

const GROUP = {
  select: "🚀 节点选择",
  manual: "📶 手动测速",
  foreign: "🌐 常见外国网页",
  websites: "网站分流",
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

function regionGroup(name, filter, providerNames, type) {
  const group = {
    name: name,
    type: type || "url-test",
    filter: filter,
  };
  if (group.type === "url-test") {
    group.url = "http://www.gstatic.com/generate_204";
    group.interval = 300;
    group.tolerance = 50;
    group.lazy = false;
  }
  if (providerNames.length) {
    group.use = providerNames;
  } else {
    group["include-all"] = true;
  }
  return group;
}

const PROVIDERS = ["airport1", "airport2"];

function buildProxyGroups(config) {
  const providerNames = PROVIDERS.filter(function (provider) {
    return config["proxy-providers"] && config["proxy-providers"][provider];
  });
  const manualGroup = {
    name: GROUP.manual,
    type: "select",
  };
  if (providerNames.length) {
    manualGroup.use = providerNames;
  } else {
    manualGroup["include-all"] = true;
  }
  const groups = [
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
    manualGroup,
  ].concat([
    {
      name: GROUP.foreign,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.websites,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.openai,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.microsoft,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.apple,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.telegram,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.youtube,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.steam,
      type: "select",
      proxies: [GROUP.select, GROUP.manual, GROUP.us, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw, "DIRECT"],
    },
    {
      name: GROUP.china,
      type: "select",
      proxies: ["DIRECT", GROUP.select, GROUP.manual, GROUP.jp, GROUP.sg, GROUP.hk, GROUP.tw],
    },
    {
      // 未命中其它规则的流量在这里单独选择出口。
      name: GROUP.fallback,
      type: "select",
      proxies: [
        GROUP.select,
        GROUP.manual,
        GROUP.foreign,
        GROUP.us,
        GROUP.jp,
        GROUP.sg,
        GROUP.hk,
        GROUP.tw,
        "DIRECT",
      ],
    },
    regionGroup(GROUP.us, "(?i)美国|US|United States|洛杉矶|纽约|西雅图|硅谷|华盛顿", providerNames, "select"),
    regionGroup(GROUP.jp, "(?i)日本|JP|Japan|东京|大阪", providerNames),
    regionGroup(GROUP.sg, "(?i)新加坡|SG|Singapore", providerNames),
    regionGroup(GROUP.hk, "(?i)香港|HK|Hong Kong", providerNames),
    regionGroup(GROUP.tw, "(?i)台湾|TW|Taiwan|台北", providerNames),
    {
      name: GROUP.blacklist,
      type: "select",
      proxies: ["REJECT", GROUP.select, GROUP.manual],
    },
  ]);
  if (providerNames.length) {
    groups.forEach(function (group) {
      group.use = providerNames;
    });
  }
  return groups;
}

function main(config) {
  config = config || {};
  config["proxy-groups"] = buildProxyGroups(config);
  return config;
}

// 方便在本地用 Node 做语法和行为测试；Clash Verge Rev 中 module 不存在。
if (typeof module !== "undefined" && module.exports) {
  module.exports = { main: main };
}
