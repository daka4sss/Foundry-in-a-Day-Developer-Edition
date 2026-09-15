"""Orchestrator agent factory.

このファイルは「ローカル実行」「Hosted Agent 実行」共通で使われる
オーケストレーションエージェントを構築する。

設計のポイント:
- 既存の Foundry 登録エージェント (Microsoft 技術専門家 / Web 検索) を
  ``FoundryAgent`` で接続し、``.as_tool()`` でツール化する。
- どのツール (= サブエージェント) を呼ぶかというルーティングロジックは
  オーケストレータの ``instructions`` には書かない。代わりに
  ``SkillsProvider`` で読み込む ``skills/orchestrator-routing/SKILL.md``
  に記載し、Agent Skills 機能経由で制御する。

English:
Orchestrator agent factory.

This file builds the orchestration agent used for both local execution and
Hosted Agent execution.

Design points:
- Connect to the existing Foundry-registered agents (the Microsoft technology
  expert and Web search agents) with ``FoundryAgent``, then convert them into
  tools with ``.as_tool()``.
- Do not define the routing logic that selects a tool (subagent) in the
  orchestrator's ``instructions``. Instead, define it in
  ``skills/orchestrator-routing/SKILL.md``, which ``SkillsProvider`` loads,
  and control routing through Agent Skills.
"""

from __future__ import annotations

import os
from pathlib import Path

from agent_framework import Agent, SkillsProvider
from agent_framework.foundry import FoundryAgent, FoundryChatClient
from azure.identity import DefaultAzureCredential

SKILLS_DIR = Path(__file__).parent / "skills"

# サブエージェントの名前 (固定。変更する場合は provision_agents.py も合わせる)
# Subagent names (fixed; update provision_agents.py as well if these change)
MS_LEARN_AGENT_NAME = "ms-learn"
WEB_SEARCH_AGENT_NAME = "web-search"

# 必須の環境変数 (未設定だとオーケストレータを構築できない)
# Required environment variables (the orchestrator cannot be built if they are unset)
REQUIRED_ENV_VARS = (
    "FOUNDRY_PROJECT_ENDPOINT",
    "AZURE_AI_MODEL_DEPLOYMENT_NAME",
)

# 意図的に最小限。ルーティング/出力フォーマットは SKILL.md 側で定義する。
# Intentionally minimal; routing and output formatting are defined in SKILL.md.
ORCHESTRATOR_INSTRUCTIONS = (
    "You are an orchestration agent. "
    "Use the available skills to decide how to answer the user."
)


def _require_env_vars() -> None:
    """必須環境変数のうち未設定のものがあれば分かりやすいエラーで停止する。"""
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise EnvironmentError(
            "次の必須環境変数が未設定です: "
            + ", ".join(missing)
            + "\n.env ファイル (ローカル実行) または "
            "`azd env set` (Hosted Agent デプロイ) で値を指定してください。"
        )


def build_orchestrator(credential=None) -> Agent:
    """オーケストレーションエージェントを構築して返す。"""
    _require_env_vars()

    if credential is None:
        credential = DefaultAzureCredential()

    project_endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

    # --- 1) サブエージェント (Prompt Agent) をツール化 ---
    # エージェント名は固定 (`scripts/provision_agents/provision_agents.py` で同名に作成)。
    # agent_version は指定しないと latest にバインドされる。
    # `allow_preview=True` は Foundry のエージェント専用エンドポイントへルーティングするために必要。
    # --- 1) Convert the subagents (Prompt Agents) into tools ---
    # Agent names are fixed (created with the same names in `scripts/provision_agents/provision_agents.py`).
    # Omitting agent_version binds to the latest version.
    # `allow_preview=True` is required to route to the Foundry agent-specific endpoint.
    ms_learn_agent = FoundryAgent(
        project_endpoint=project_endpoint,
        agent_name=MS_LEARN_AGENT_NAME,
        credential=credential,
        allow_preview=True,
    )
    web_search_agent = FoundryAgent(
        project_endpoint=project_endpoint,
        agent_name=WEB_SEARCH_AGENT_NAME,
        credential=credential,
        allow_preview=True,
    )

    # SKILL.md からツール名で参照されるので、name を固定する。
    # Keep each name fixed because SKILL.md references the tools by name.
    ms_learn_tool = ms_learn_agent.as_tool(
        name="ms_learn_agent",
        description=(
            "Microsoft 技術 (Azure / Microsoft 365 / .NET / Windows / "
            "Microsoft Foundry など) の質問に Microsoft Learn ベースで回答する専門家エージェント。"
        ),
        arg_name="question",
        arg_description="Microsoft 技術に関する質問文",
    )
    web_search_tool = web_search_agent.as_tool(
        name="web_search_agent",
        description=(
            "Web 検索を行って一般的な事実・最新情報・"
            "Microsoft 以外のトピックに回答する汎用エージェント。"
        ),
        arg_name="question",
        arg_description="Web 検索したい質問文",
    )

    # --- 2) オーケストレータ用 LLM クライアント ---
    # --- 2) LLM client for the orchestrator ---
    chat_client = FoundryChatClient(
        project_endpoint=project_endpoint,
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=credential,
    )

    # --- 3) Agent Skills プロバイダー ---
    # 最新 SDK ではファイルベースの skill を `from_paths(...)` で読み込む。
    # --- 3) Agent Skills provider ---
    # The latest SDK loads file-based skills with `from_paths(...)`.
    skills_provider = SkillsProvider.from_paths(skill_paths=str(SKILLS_DIR))

    # --- 4) オーケストレーションエージェント ---
    # --- 4) Orchestration agent ---
    return Agent(
        client=chat_client,
        name="OrchestratorAgent",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        tools=[ms_learn_tool, web_search_tool],
        context_providers=[skills_provider],
        # Hosted 実行時、履歴はホスティング基盤側で管理されるため
        # サービス側に保存しない。
        # When hosted, the hosting platform manages history,
        # so do not store it in the service.
        default_options={"store": False},
    )
