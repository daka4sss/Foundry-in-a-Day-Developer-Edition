"""Foundry Hosted Agent 用エントリポイント。

``ResponsesHostServer`` でオーケストレータをラップし、
ポート 8088 で Responses プロトコル (POST /responses) を提供する。
Foundry プラットフォームが ``FOUNDRY_PROJECT_ENDPOINT`` などの
環境変数を自動注入するため、ここでは追加設定不要。

English:
Entry point for the Foundry Hosted Agent.

Wraps the orchestrator with ``ResponsesHostServer`` and provides the
Responses protocol (POST /responses) on port 8088. The Foundry platform
automatically injects environment variables such as
``FOUNDRY_PROJECT_ENDPOINT``, so no additional configuration is required here.
"""

from __future__ import annotations

from agent_framework_foundry_hosting import ResponsesHostServer
from dotenv import load_dotenv

from orchestrator import build_orchestrator


def main() -> None:
    # ローカル動作確認用。Hosted では実質 no-op。
    # Used for local testing; effectively a no-op when hosted.
    load_dotenv()
    agent = build_orchestrator()
    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    main()
