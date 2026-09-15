"""ローカル実行用エントリポイント。

使い方:
  az login                       # Azure CLI で先にログイン
  cd agent-src
  python -m venv .venv && .\\.venv\\Scripts\\Activate.ps1  # Windows
  pip install -r requirements.txt
  python local.py

English:
Local execution entry point.

Usage:
  az login                       # Sign in with Azure CLI first
  cd agent-src
  python -m venv .venv && .\\.venv\\Scripts\\Activate.ps1  # Windows
  pip install -r requirements.txt
  python local.py
"""

from __future__ import annotations

import asyncio

from dotenv import find_dotenv, load_dotenv

from orchestrator import build_orchestrator

# 標準出力に「呼び出されたサブエージェント」を表示するためのツール名集合
# Tool names used to show the invoked subagents in standard output
SUB_AGENT_TOOL_NAMES = {"ms_learn_agent", "web_search_agent"}


def _called_sub_agents(result) -> list[str]:
    """応答メッセージから、呼び出されたサブエージェントのツール名を順序を保って抽出する。"""
    seen: list[str] = []
    for msg in getattr(result, "messages", []) or []:
        for content in getattr(msg, "contents", []) or []:
            if getattr(content, "type", None) == "function_call":
                name = getattr(content, "name", None)
                if name in SUB_AGENT_TOOL_NAMES and name not in seen:
                    seen.append(name)
    return seen


async def main() -> None:
    # find_dotenv() は呼び出し元から親ディレクトリへ探索する。
    # find_dotenv() searches parent directories from the caller.
    load_dotenv(find_dotenv(usecwd=True))
    agent = build_orchestrator()

    print("Orchestrator ready. 終了するには 'exit' / 'quit' / Ctrl+C。\n")
    while True:
        try:
            user = input("User> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            break

        result = await agent.run(user)
        print(f"\nAgent>\n{result.text}\n")

        called = _called_sub_agents(result)
        called_str = ", ".join(called) if called else "(none)"
        print(f"[呼び出されたサブエージェント: {called_str}]\n")


if __name__ == "__main__":
    asyncio.run(main())
