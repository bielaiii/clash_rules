#!/usr/bin/env node
"use strict";

const assert = require("assert");
const { main } = require("../global_script.js");

const input = {
  proxies: [
    { name: "美国-01", type: "ss", server: "us.example.com" },
    { name: "日本-01", type: "ss", server: "jp.example.com" },
  ],
  rules: ["MATCH,DIRECT"],
  "rule-providers": { Existing: { type: "http" }, Google: { stale: true } },
};

const output = main(input);
const groupNames = output["proxy-groups"].map((group) => group.name);
const groups = new Map(output["proxy-groups"].map((group) => [group.name, group]));

function assertNoGroupLoop(name, path) {
  assert(!path.includes(name), `proxy group loop: ${path.concat(name).join(" -> ")}`);
  const group = groups.get(name);
  if (!group) return;
  (group.proxies || []).forEach((proxy) => {
    if (groups.has(proxy)) assertNoGroupLoop(proxy, path.concat(name));
  });
}

assert.strictEqual(output["proxy-groups"].find((group) => group.name === "📶 手动测速")["include-all"], true);
assert(groupNames.includes("🚀 节点选择"));
assert(groupNames.includes("🐟 漏网之鱼"));
assert.strictEqual(output["rule-providers"].Existing.type, "http");
assert.strictEqual(output["rule-providers"].Google.stale, true);
assert.deepStrictEqual(output.rules, ["MATCH,DIRECT"]);
groupNames.forEach((name) => assertNoGroupLoop(name, []));
["🇺🇸 美国地区", "🇯🇵 日本地区", "🇸🇬 新加坡地区", "🇭🇰 香港地区", "🇹🇼 台湾地区"].forEach((name) => {
  const group = groups.get(name);
  assert(!group.proxies || !group.proxies.includes("📶 手动测速"));
});
["🌐 常见外国网页", "🤖 OpenAI", "Ⓜ️ Microsoft", "🍎 Apple", "📲 Telegram", "📺 YouTube", "🎮 Steam"].forEach((name) => {
  const group = groups.get(name);
  assert(group.proxies.includes("📶 手动测速"));
  assert(group.proxies.includes("🚀 节点选择"));
  assert(group.proxies.includes("🇺🇸 美国地区"));
  assert(group.proxies.includes("🇯🇵 日本地区"));
  assert(group.proxies.includes("🇸🇬 新加坡地区"));
  assert(group.proxies.includes("🇭🇰 香港地区"));
  assert(group.proxies.includes("🇹🇼 台湾地区"));
});

// 覆写模式下全部节点来自 provider；同时覆盖仅有第二机场的情况。
for (const providerNames of [["airport1"], ["airport2"], ["airport1", "airport2"]]) {
  const config = {
    "proxy-providers": Object.fromEntries(providerNames.map((name) => [name, { type: "http" }])),
    rules: ["DOMAIN-SUFFIX,pixiv.net,🌐 常见外国网页", "MATCH,🐟 漏网之鱼"],
  };
  const originalRules = config.rules.slice();
  const result = main(config);
  assert.deepStrictEqual(result.rules, originalRules);
  result["proxy-groups"].forEach((group) => {
    assert.deepStrictEqual(group.use, providerNames, `${group.name}: missing airport provider`);
    assert(!group["include-all"], `${group.name}: unexpected subscription node mixing`);
    if (group.type === "url-test") {
      assert.strictEqual(group.lazy, false, `${group.name}: should test before first use`);
      assert.strictEqual(group.interval, 300);
    }
  });
  assert.strictEqual(result["proxy-groups"].find((group) => group.name === "🇺🇸 美国地区").type, "select");
}

console.log("global extension script passed");
