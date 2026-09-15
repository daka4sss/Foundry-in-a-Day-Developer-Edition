"""Foundry に 2 つの Prompt Agent を作成するセットアップスクリプト。

このスクリプトは、本ワークショップで利用する次の 2 つのエージェントを
Microsoft Foundry プロジェクトに作成 (またはバージョン追加) する:

1. Microsoft 技術専門家エージェント (固定名: ``ms-learn``)
   - Microsoft Learn MCP サーバー (https://learn.microsoft.com/api/mcp) を
     ``MCPTool`` として接続し、Microsoft 技術に関する質問に対し
     Microsoft Learn ドキュメントに基づいて回答する。

2. Web 検索エージェント (固定名: ``web-search``)
   - Foundry Agent Service の ``WebSearchTool`` (Bing Search グラウンディング)
     を使い、最新の一般的な Web 情報に基づいて回答する。

エージェント名はオーケストレータ側 (``agent-src/orchestrator.py``) と
合わせて固定値にしている (名前を変えたい場合は両方修正すること)。

このスクリプトはリポジトリルートの ``.env`` を読み込み、
``FOUNDRY_PROJECT_ENDPOINT`` / ``AZURE_AI_MODEL_DEPLOYMENT_NAME`` のみ参照する。

使い方:
  cd scripts/provision_agents
  python -m venv .venv
  # Windows
  .\\.venv\\Scripts\\Activate.ps1
  # Linux / macOS
  source .venv/bin/activate
  pip install -r requirements.txt
  az login
  python provision_agents.py

English:
Setup script that creates two Prompt Agents in Foundry.

This script creates (or adds a version to) the following two agents used in
this workshop in a Microsoft Foundry project:

1. Microsoft technology expert agent (fixed name: ``ms-learn``)
   - Connects to the Microsoft Learn MCP server
     (https://learn.microsoft.com/api/mcp) as an ``MCPTool`` and answers
     questions about Microsoft technology based on Microsoft Learn
     documentation.

2. Web search agent (fixed name: ``web-search``)
   - Uses the Foundry Agent Service ``WebSearchTool`` (Bing Search grounding)
     to answer based on current, general information from the Web.

The agent names are fixed to match the orchestrator
(``agent-src/orchestrator.py``). Update both locations if you change a name.

This script loads ``.env`` from the repository root and reads only
``FOUNDRY_PROJECT_ENDPOINT`` and ``AZURE_AI_MODEL_DEPLOYMENT_NAME``.

Usage:
  cd scripts/provision_agents
  python -m venv .venv
  # Windows
  .\\.venv\\Scripts\\Activate.ps1
  # Linux / macOS
  source .venv/bin/activate
  pip install -r requirements.txt
  az login
  python provision_agents.py
"""

from __future__ import annotations

import os
import sys

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    WebSearchApproximateLocation,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import find_dotenv, load_dotenv

# サブエージェントの名前 (固定。orchestrator.py の定数と一致させる)
# Subagent names (fixed; keep them aligned with the constants in orchestrator.py)
MS_LEARN_AGENT_NAME = "ms-learn"
WEB_SEARCH_AGENT_NAME = "web-search"

# Microsoft Learn の公開 MCP エンドポイント (認証不要)
# Public Microsoft Learn MCP endpoint (no authentication required)
MS_LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"

MS_LEARN_INSTRUCTIONS = (
    "あなたは Microsoft 技術 (Azure / Microsoft 365 / .NET / Windows / "
    "Microsoft Foundry など) の専門家エージェントです。"
    "ユーザーからの質問に対しては必ず Microsoft Learn MCP サーバーを呼び出し、"
    "Microsoft Learn ドキュメントの最新情報を根拠として簡潔に回答してください。"
    "回答には参照した Microsoft Learn のページタイトルと URL を必ず明示してください。"
)

WEB_SEARCH_INSTRUCTIONS = (
    "あなたは Web 検索を使って一般的な質問に答えるアシスタントです。"
    "ユーザーからの質問に対しては常に Web 検索ツールを使い、"
    "最新の公開情報に基づいて簡潔に回答してください。"
    "回答には参照した Web ページのタイトルと URL を必ず明示してください。"
)

REQUIRED_ENV_VARS = (
    "FOUNDRY_PROJECT_ENDPOINT",
    "AZURE_AI_MODEL_DEPLOYMENT_NAME",
)


def _require_env() -> None:
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        sys.exit(
            "次の必須環境変数が未設定です: "
            + ", ".join(missing)
            + "\nリポジトリルートの .env を作成 (もしくは編集) してから再実行してください。"
        )


def _create_ms_learn_agent(project: AIProjectClient, *, model: str) -> None:
    print(f"[{MS_LEARN_AGENT_NAME}] Microsoft Learn MCP ツール付きの Prompt Agent を作成中 ...")
    mcp_tool = MCPTool(
        server_label="microsoft-learn",
        server_url=MS_LEARN_MCP_URL,
        # オーケストレータから自動で呼び出すため承認は不要
        # Approval is unnecessary because the orchestrator invokes this automatically.
        require_approval="never",
    )
    agent = project.agents.create_version(
        agent_name=MS_LEARN_AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=MS_LEARN_INSTRUCTIONS,
            tools=[mcp_tool],
        ),
        description="Microsoft 技術専門家 (Microsoft Learn MCP)",
    )
    print(f"  ✓ created: id={agent.id}, name={agent.name}, version={agent.version}")


def _create_web_search_agent(project: AIProjectClient, *, model: str) -> None:
    print(f"[{WEB_SEARCH_AGENT_NAME}] WebSearchTool 付きの Prompt Agent を作成中 ...")
    web_tool = WebSearchTool(
        user_location=WebSearchApproximateLocation(
            country="JP", city="Tokyo", region="Tokyo"
        ),
    )
    agent = project.agents.create_version(
        agent_name=WEB_SEARCH_AGENT_NAME,
        definition=PromptAgentDefinition(
            model=model,
            instructions=WEB_SEARCH_INSTRUCTIONS,
            tools=[web_tool],
        ),
        description="Web 検索エージェント (Foundry WebSearchTool)",
    )
    print(f"  ✓ created: id={agent.id}, name={agent.name}, version={agent.version}")


def main() -> None:
    # リポジトリルート (scripts/provision_agents の 2 階層上) の .env を探して読み込む
    # Find and load .env from the repository root (two levels above scripts/provision_agents).
    load_dotenv(find_dotenv(usecwd=True))
    _require_env()

    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

    print(f"Foundry project endpoint: {project_endpoint}")
    print(f"Model deployment        : {model}\n")

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    _create_ms_learn_agent(project, model=model)
    print()
    _create_web_search_agent(project, model=model)

    print("\n完了しました。Foundry ポータルの「エージェント」一覧で確認してください。")


if __name__ == "__main__":
    main()
