#!/usr/bin/env python3
"""
Claude Subscription Usage Checker
查詢 Claude Pro/Max 訂閱的剩餘用量

使用方式:
    # 透過 CLI 命令
    claude-usage

    # 或直接執行
    python -m luminnexus_alchemy_shared.claude_usage

    # 使用 uv
    uv run claude-usage

Token 來源:
    自動從系統讀取 Claude Code 的 credentials
    - macOS: Keychain Access
    - Linux: ~/.claude/credentials.json
"""

import argparse
import json
import platform
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def get_credentials_macos() -> Optional[str]:
    """從 macOS Keychain 取得 Claude Code credentials"""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "Claude Code-credentials", "-w"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None


def get_credentials_linux() -> Optional[str]:
    """從 Linux 檔案系統讀取 Claude Code credentials

    Claude Code 在 Linux 上儲存 credentials 於 ~/.claude/.credentials.json
    """
    credentials_path = Path.home() / ".claude" / ".credentials.json"

    if credentials_path.exists():
        try:
            return credentials_path.read_text().strip()
        except Exception:
            pass

    return None


def get_access_token(token_arg: Optional[str] = None) -> Optional[str]:
    """
    取得 OAuth access token

    優先順序:
    1. 命令列參數 --token
    2. 系統 Keychain (macOS) / secret-tool (Linux)
    """
    # 1. 命令列參數
    if token_arg:
        return token_arg

    # 2. 系統 Keychain
    system = platform.system()

    if system == "Darwin":  # macOS
        creds_json = get_credentials_macos()
    elif system == "Linux":
        creds_json = get_credentials_linux()
    else:
        print(f"❌ 不支援的作業系統: {system}")
        return None

    if not creds_json:
        print("❌ 找不到 Claude Code credentials")
        print()
        print("   請先登入 Claude Code:")
        print("   $ claude login")
        print()
        print("   或使用 --token 參數手動提供 token:")
        print("   $ claude-usage --token sk-ant-xxx")
        return None

    try:
        creds = json.loads(creds_json)
        token = creds.get("claudeAiOauth", {}).get("accessToken")
        if not token:
            print("❌ Credentials 中沒有 accessToken")
            print("   請重新登入: claude logout && claude login")
            return None
        return token
    except json.JSONDecodeError as e:
        print(f"❌ 無法解析 credentials JSON: {e}")
        return None


def fetch_usage(token: str) -> Optional[dict]:
    """呼叫 API 取得用量資訊"""
    url = "https://api.anthropic.com/api/oauth/usage"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "anthropic-beta": "oauth-2025-04-20",
        "User-Agent": "claude-code/2.0.31",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("❌ Token 已過期或無效")
            print("   請重新登入 Claude Code: claude logout && claude login")
        else:
            print(f"❌ API 錯誤: HTTP {e.code}")
        return None
    except urllib.error.URLError as e:
        print(f"❌ 網路錯誤: {e.reason}")
        return None


def format_reset_time(reset_at: Optional[str]) -> str:
    """格式化重置時間"""
    if not reset_at:
        return "N/A"

    try:
        reset_time = datetime.fromisoformat(reset_at.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = reset_time - now

        if diff.total_seconds() < 0:
            return "即將重置"

        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes = remainder // 60

        if hours > 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}天 {hours}小時後"
        elif hours > 0:
            return f"{hours}小時 {minutes}分鐘後"
        else:
            return f"{minutes}分鐘後"
    except Exception:
        return reset_at


def print_usage_rich(usage: dict):
    """使用 rich 輸出漂亮的用量資訊"""
    console = Console()

    console.print("\n[bold cyan]═══ Claude 訂閱用量 ═══[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("週期", style="cyan", width=12)
    table.add_column("已使用", justify="right", width=10)
    table.add_column("剩餘", justify="right", width=10)
    table.add_column("進度條", width=25)
    table.add_column("重置時間", width=18)

    for period_name, period_key in [("5 小時", "five_hour"), ("7 天", "seven_day")]:
        period_data = usage.get(period_key)

        if period_data:
            # utilization 已經是百分比（例如 55 代表 55%）
            used_pct = period_data.get("utilization", 0)
            remaining_pct = max(0, 100 - used_pct)
            reset_time = format_reset_time(period_data.get("resets_at"))

            # 進度條顏色
            if used_pct >= 90:
                bar_color = "red"
            elif used_pct >= 70:
                bar_color = "yellow"
            else:
                bar_color = "green"

            # 建立文字進度條
            bar_width = 20
            filled = int(bar_width * used_pct / 100)
            empty = bar_width - filled
            bar = f"[{bar_color}]{'█' * filled}[/{bar_color}][dim]{'░' * empty}[/dim]"

            table.add_row(
                period_name,
                f"[bold]{used_pct:.1f}%[/bold]",
                f"[green]{remaining_pct:.1f}%[/green]",
                bar,
                reset_time,
            )
        else:
            table.add_row(period_name, "N/A", "N/A", "", "N/A")

    console.print(table)
    console.print()


def print_usage_simple(usage: dict):
    """簡單文字輸出用量資訊"""
    print("\n" + "=" * 50)
    print("        Claude 訂閱用量")
    print("=" * 50)

    for period_name, period_key in [("5 小時週期", "five_hour"), ("7 天週期", "seven_day")]:
        period_data = usage.get(period_key)
        print(f"\n📊 {period_name}:")

        if period_data:
            # utilization 已經是百分比（例如 55 代表 55%）
            used_pct = period_data.get("utilization", 0)
            remaining_pct = max(0, 100 - used_pct)
            reset_time = format_reset_time(period_data.get("resets_at"))

            # 文字進度條
            bar_width = 30
            filled = int(bar_width * used_pct / 100)
            empty = bar_width - filled
            bar = "█" * filled + "░" * empty

            # 狀態 emoji
            if used_pct >= 90:
                status = "🔴"
            elif used_pct >= 70:
                status = "🟡"
            else:
                status = "🟢"

            print(f"   {status} 已使用: {used_pct:.1f}% | 剩餘: {remaining_pct:.1f}%")
            print(f"   [{bar}]")
            print(f"   ⏰ 重置時間: {reset_time}")
        else:
            print("   ⚠️  無資料")

    print("\n" + "=" * 50 + "\n")


def print_usage_json(usage: dict):
    """JSON 格式輸出"""
    print(json.dumps(usage, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="查詢 Claude Pro/Max 訂閱用量",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Token 來源:
  自動從系統 Keychain 讀取 (需先執行 claude login)

範例:
  claude-usage                    # 自動從 Keychain 讀取 token
  claude-usage --token sk-xxx     # 手動提供 token
  claude-usage --json             # JSON 格式輸出
  claude-usage --simple           # 簡單文字輸出
        """,
    )
    parser.add_argument("--token", "-t", help="手動提供 access token（覆蓋系統 Keychain）")
    parser.add_argument("--json", "-j", action="store_true", help="以 JSON 格式輸出")
    parser.add_argument("--simple", "-s", action="store_true", help="簡單文字輸出（不使用 rich）")
    args = parser.parse_args()

    # 取得 token
    token = get_access_token(args.token)
    if not token:
        sys.exit(1)

    # 取得用量
    usage = fetch_usage(token)
    if not usage:
        sys.exit(1)

    # 輸出
    if args.json:
        print_usage_json(usage)
    elif args.simple or not RICH_AVAILABLE:
        print_usage_simple(usage)
    else:
        print_usage_rich(usage)


if __name__ == "__main__":
    main()
