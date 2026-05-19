# Copyright (c) Microsoft. All rights reserved.
# 演習1: Foundry SDK でエージェントと対話する

import os

from azure.ai.projects import AIProjectClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込み
load_dotenv()

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
AGENT_NAME = os.environ.get("MICROSOFT_FOUNDRY_AGENT_NAME", "zava-support-agent-x")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")


def main():
    """作成済みの Prompt Agent と対話する"""
    # プロジェクトクライアントの作成
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=AzureCliCredential(tenant_id=TENANT_ID),
    )

    # OpenAI 互換クライアントを取得
    openai = project.get_openai_client()

    # マルチターン会話を開始
    conversation = openai.conversations.create()
    print(f"🔗 Conversation started (ID: {conversation.id})")
    print(f"🤖 Agent: {AGENT_NAME}")
    print("-" * 50)

    # 1回目の質問
    print("\n📤 User: 顧客ID C001 の最近の注文について教えてください")
    response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        input="顧客ID C001 の最近の注文について教えてください",
    )
    print(f"📥 Agent: {response.output_text}")

    # 2回目の質問（マルチターン）
    print("\n📤 User: その注文のステータスを確認してもらえますか？")
    response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        input="その注文のステータスを確認してもらえますか？",
    )
    print(f"📥 Agent: {response.output_text}")

    # 3回目の質問
    print("\n📤 User: 返品ポリシーについて教えてください")
    response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": AGENT_NAME, "type": "agent_reference"}},
        input="返品ポリシーについて教えてください",
    )
    print(f"📥 Agent: {response.output_text}")

    print("\n" + "-" * 50)
    print("✅ マルチターン会話のテスト完了!")


if __name__ == "__main__":
    main()
