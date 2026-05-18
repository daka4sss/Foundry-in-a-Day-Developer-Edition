# Copyright (c) Microsoft. All rights reserved.
# 演習1: Foundry SDK で Prompt Agent を作成する

import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込み
load_dotenv()

PROJECT_ENDPOINT = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
AGENT_NAME = os.environ.get("MICROSOFT_FOUNDRY_AGENT_NAME", "zava-support-agent-x")
MODEL_DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1-mini")
TENANT_ID = os.environ.get("AZURE_TENANT_ID")

# Zava カスタマーサポート用のシステムプロンプト
AGENT_INSTRUCTIONS = """あなたは Zava 社のカスタマーサポートエージェントです。

## 役割
- 顧客からの問い合わせに丁寧に対応する
- 注文履歴の確認、FAQ の案内、問題のエスカレーション判定を行う

## 対応ガイドライン
1. まず顧客の問題を正確に把握する
2. 注文関連の問い合わせには注文履歴を確認する
3. よくある質問は FAQ から回答する
4. 複雑な問題や顧客が不満を表明している場合はエスカレーションを検討する
5. 常に丁寧で共感的な対応を心がける

## 制約
- 個人情報の取り扱いには注意する
- 確認できない情報は推測せず、確認する旨を伝える
"""


def main():
    """Foundry プロジェクトに Prompt Agent を作成する"""
    # プロジェクトクライアントの作成
    project = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=AzureCliCredential(tenant_id=TENANT_ID),
    )

    # エージェントの作成
    agent = project.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=AGENT_INSTRUCTIONS,
        ),
    )

    print(f"✅ Agent created successfully!")
    print(f"   Name:    {agent.name}")
    print(f"   ID:      {agent.id}")
    print(f"   Version: {agent.version}")
    print(f"   Model:   {MODEL_DEPLOYMENT}")
    print(f"\n💡 次のステップ: 02_chat_with_agent.py でエージェントと対話してみましょう")


if __name__ == "__main__":
    main()
