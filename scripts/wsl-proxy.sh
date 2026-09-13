#!/usr/bin/env bash
# Load Windows-host proxy settings into the current WSL shell.
# Usage: source scripts/wsl-proxy.sh

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "请使用: source scripts/wsl-proxy.sh" >&2
  exit 1
fi

proxy_port="${CLASH_PROXY_PORT:-7890}"
windows_host="${WIN_PROXY_HOST:-}"

if [[ -z "$windows_host" ]] && command -v powershell.exe >/dev/null 2>&1; then
  windows_host="$(powershell.exe -NoProfile -Command \
    "(Get-NetIPConfiguration | Where-Object { \$_.IPv4DefaultGateway -ne \$null -and \$_.NetAdapter.Status -eq 'Up' } | ForEach-Object { \$_.IPv4Address.IPAddress } | Select-Object -First 1)" \
    2>/dev/null | tr -d '\r' | head -n 1)"
fi

# WSL's resolv.conf commonly points at the Windows-side DNS/host gateway.
if [[ -z "$windows_host" ]] && [[ -r /etc/resolv.conf ]]; then
  windows_host="$(awk '/^nameserver / {print $2; exit}' /etc/resolv.conf)"
fi

if [[ -z "$windows_host" ]]; then
  echo "无法自动获取 Windows 主机 IP。请执行: WIN_PROXY_HOST=你的Windows_IP source scripts/wsl-proxy.sh" >&2
  return 1
fi

export HTTP_PROXY="http://${windows_host}:${proxy_port}"
export HTTPS_PROXY="$HTTP_PROXY"
export ALL_PROXY="socks5h://${windows_host}:${proxy_port}"
export http_proxy="$HTTP_PROXY"
export https_proxy="$HTTPS_PROXY"
export all_proxy="$ALL_PROXY"
export NO_PROXY="localhost,127.0.0.1,::1"

echo "WSL proxy: ${windows_host}:${proxy_port}"
echo "现在请在当前终端启动 Codex；如端口不对，可先设置 CLASH_PROXY_PORT=7897 再 source 本脚本。"
