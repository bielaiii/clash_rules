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
  assert(!group.proxies.includes("📶 手动测速"));
  assert(group.proxies.includes("🚀 节点选择"));
  assert(group.proxies.includes("🇺🇸 美国地区"));
  assert(group.proxies.includes("🇯🇵 日本地区"));
  assert(group.proxies.includes("🇸🇬 新加坡地区"));
  assert(group.proxies.includes("🇭🇰 香港地区"));
  assert(group.proxies.includes("🇹🇼 台湾地区"));
});

console.log("global extension script passed");
