# Copyright (c) Microsoft. All rights reserved.
# 演習 3: MAF から Foundry の Prompt Agent (演習 1.4 で作成) を呼び出す
#
# MAF には Foundry に登録済みのエージェントを直接呼び出すクラス FoundryAgent が
# 用意されている。内部で `agent_reference` を自動付与してくれるため、
# 自前で AIProjectClient + openai.responses.create(...) を書く必要がない。
#
# Exercise 3: Invoke the Foundry Prompt Agent created in Exercise 1.4 from MAF
#
# MAF provides FoundryAgent, a class that directly invokes agents registered in Foundry.
# It automatically adds `agent_reference` internally, so there is no need to implement
# AIProjectClient + openai.responses.create(...) yourself.

import asyncio
import logging
import os

from agent_framework_foundry import FoundryAgent
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
PROMPT_AGENT_NAME = os.environ.get("MICROSOFT_FOUNDRY_AGENT_NAME", "zava-support-agent-x")
# PromptAgent では必須
# Required for PromptAgent
PROMPT_AGENT_VERSION = os.environ.get("AZURE_AI_FOUNDRY_AGENT_VERSION")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")


async def main():
    credential = AzureCliCredential(tenant_id=TENANT_ID) if TENANT_ID else AzureCliCredential()
    async with credential:
        # MAF の FoundryAgent: Foundry に登録済みのエージェントを名前で参照する公式クライアント
        # MAF FoundryAgent: the official client for referencing a Foundry-registered agent by name
        agent = FoundryAgent(
            project_endpoint=PROJECT_ENDPOINT,
            agent_name=PROMPT_AGENT_NAME,
            # agent_name: PromptAgent では必須 (HostedAgent は省略可)
            # agent_name: Required for PromptAgent (optional for HostedAgent)
            agent_version=PROMPT_AGENT_VERSION,
            credential=credential,
        )

        # マルチターン会話を維持するためのセッション
        # Session used to maintain a multi-turn conversation
        session = agent.create_session()

        questions = [
            "顧客ID C001 の最近の注文を教えてください",
            "その注文がまだ届いていないようなのですが、ステータスを確認できますか？",
            "返品ポリシーについても教えてください",
        ]

        print("=" * 60)
        print(f"MAF FoundryAgent → Foundry Prompt Agent ({PROMPT_AGENT_NAME})")
        print("=" * 60)

        for i, q in enumerate(questions, 1):
            print(f"\n--- ターン {i} ---")
            print(f"📤 User : {q}")
            response = await agent.run(q, session=session)
            print(f"📥 Agent: {response.text}")

        print("\n" + "=" * 60)
        print("✅ 全ターン完了")


if __name__ == "__main__":
    asyncio.run(main())
