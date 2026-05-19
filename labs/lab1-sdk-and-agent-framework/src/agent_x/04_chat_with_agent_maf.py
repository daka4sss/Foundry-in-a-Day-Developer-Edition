# Copyright (c) Microsoft. All rights reserved.
# 演習 3: MAF から Foundry の Prompt Agent (演習 1.4 で作成) を呼び出す
#
# MAF には Foundry に登録済みのエージェントを直接呼び出すクラス FoundryAgent が
# 用意されている。内部で `agent_reference` を自動付与してくれるため、
# 自前で AIProjectClient + openai.responses.create(...) を書く必要がない。

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
PROMPT_AGENT_VERSION = os.environ.get("AZURE_AI_FOUNDRY_AGENT_VERSION")  # PromptAgent では必須
TENANT_ID = os.environ.get("AZURE_TENANT_ID")


async def main():
    credential = AzureCliCredential(tenant_id=TENANT_ID) if TENANT_ID else AzureCliCredential()
    async with credential:
        # MAF の FoundryAgent: Foundry に登録済みのエージェントを名前で参照する公式クライアント
        agent = FoundryAgent(
            project_endpoint=PROJECT_ENDPOINT,
            agent_name=PROMPT_AGENT_NAME,
            agent_version=PROMPT_AGENT_VERSION,  # PromptAgent では必須 (HostedAgent は省略可)
            credential=credential,
        )

        # マルチターン会話を維持するためのセッション
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
