# Copyright (c) Microsoft. All rights reserved.
# 演習2: MAF で Agent X を構築する (Microsoft Learn MCP 連携付き)
# Zava カスタマーサポート専門エージェント

import importlib
import logging
import os

from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# SDK 互換性フィックス (起動時に1回だけ適用)
# agent-framework-foundry-hosting が空の ChatOptions を agent.run() に
# 渡す問題を修正する。ライブラリ側の修正が取り込まれたら削除して良い。
# ---------------------------------------------------------------------------
def _ensure_hosting_compat():
    try:
        import agent_framework_foundry_hosting._responses as mod
    except ImportError:
        return

    with open(mod.__file__, "r", encoding="utf-8") as f:
        content = f.read()

    old = (
        '        if are_options_set and not isinstance(self._agent, RawAgent):\n'
        '            logger.warning("Agent doesn\'t support runtime options. They will be ignored.")\n'
        '        else:\n'
        '            run_kwargs["options"] = chat_options'
    )
    new = (
        '        if are_options_set:\n'
        '            if isinstance(self._agent, RawAgent):\n'
        '                run_kwargs["options"] = chat_options\n'
        '            else:\n'
        '                logger.warning("Agent doesn\'t support runtime options. They will be ignored.")'
    )

    if old in content:
        with open(mod.__file__, "w", encoding="utf-8") as f:
            f.write(content.replace(old, new))
        importlib.reload(mod)


_ensure_hosting_compat()

from agent_framework import Agent, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity.aio import AzureCliCredential, DefaultAzureCredential
from pydantic import Field
from typing_extensions import Annotated

# .env ファイルから環境変数を読み込み (Foundry 注入の変数が優先される)
load_dotenv(override=False)

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# サンプルデータ (本番ではデータベースや API に置き換え)
# =============================================================================

ORDER_DATABASE = {
    "C001": [
        {"order_id": "ORD-2024-001", "date": "2024-12-15", "items": ["ワイヤレスイヤホン"], "status": "配送済み", "amount": 12800},
        {"order_id": "ORD-2025-002", "date": "2025-01-20", "items": ["スマートウォッチ", "充電ケーブル"], "status": "配送中", "amount": 35600},
        {"order_id": "ORD-2025-003", "date": "2025-02-10", "items": ["ノイズキャンセリングヘッドホン"], "status": "処理中", "amount": 28900},
    ],
    "C002": [
        {"order_id": "ORD-2025-004", "date": "2025-01-05", "items": ["USB-C ハブ"], "status": "配送済み", "amount": 5400},
        {"order_id": "ORD-2025-005", "date": "2025-02-28", "items": ["モニターアーム", "デスクマット"], "status": "配送済み", "amount": 18200},
    ],
}

FAQ_DATABASE = {
    "返品": "返品は商品到着後14日以内であれば承ります。未開封・未使用の商品に限ります。返品送料はお客様負担となります。",
    "配送": "通常配送は注文から3-5営業日、お急ぎ便は1-2営業日でお届けします。配送状況はマイページからご確認いただけます。",
    "支払い方法": "クレジットカード(VISA/Mastercard/AMEX)、デビットカード、コンビニ払い、銀行振込に対応しています。",
    "キャンセル": "注文確定後30分以内であればマイページからキャンセル可能です。それ以降は配送準備に入るためキャンセルできません。",
    "保証": "電子機器は購入日から1年間のメーカー保証が付きます。保証期間内の自然故障は無償修理・交換対応いたします。",
    "ポイント": "お買い物金額の1%がポイントとして付与されます。1ポイント=1円として次回以降のお買い物にご利用いただけます。",
}


# =============================================================================
# ツール定義
# =============================================================================

@tool(approval_mode="never_require")
def search_order_history(
    customer_id: Annotated[str, Field(description="顧客ID (例: C001)")],
) -> str:
    """顧客の注文履歴を検索します。顧客IDを指定して過去の注文情報を取得します。"""
    orders = ORDER_DATABASE.get(customer_id)
    if not orders:
        return f"顧客ID '{customer_id}' の注文履歴は見つかりませんでした。"

    result = f"顧客ID: {customer_id} の注文履歴 ({len(orders)}件):\n\n"
    for order in orders:
        result += f"- 注文番号: {order['order_id']}\n"
        result += f"  日付: {order['date']}\n"
        result += f"  商品: {', '.join(order['items'])}\n"
        result += f"  金額: ¥{order['amount']:,}\n"
        result += f"  ステータス: {order['status']}\n\n"
    return result


@tool(approval_mode="never_require")
def search_faq(
    keyword: Annotated[str, Field(description="検索キーワード (例: 返品, 配送, 支払い)")],
) -> str:
    """FAQ データベースからキーワードに一致する回答を検索します。"""
    results = []
    for topic, answer in FAQ_DATABASE.items():
        if keyword in topic or keyword in answer:
            results.append(f"【{topic}】\n{answer}")

    if not results:
        return f"キーワード '{keyword}' に一致する FAQ は見つかりませんでした。別のキーワードで検索するか、オペレーターへのエスカレーションをご検討ください。"

    return "FAQ 検索結果:\n\n" + "\n\n".join(results)


@tool(approval_mode="never_require")
def check_escalation_needed(
    issue_description: Annotated[str, Field(description="問題の説明")],
    customer_sentiment: Annotated[str, Field(description="顧客の感情 (positive/neutral/negative/angry)")],
) -> str:
    """問題の内容と顧客の感情に基づき、人間のオペレーターへのエスカレーションが必要か判定します。"""
    escalation_keywords = ["クレーム", "訴訟", "消費者庁", "返金", "詐欺", "壊れ", "不良品"]
    needs_escalation = False
    reasons = []

    # 感情による判定
    if customer_sentiment in ("negative", "angry"):
        needs_escalation = True
        reasons.append(f"顧客の感情が '{customer_sentiment}' と検知されました")

    # キーワードによる判定
    for kw in escalation_keywords:
        if kw in issue_description:
            needs_escalation = True
            reasons.append(f"エスカレーション対象キーワード '{kw}' が検出されました")

    if needs_escalation:
        return (
            "⚠️ エスカレーション推奨\n"
            f"理由: {'; '.join(reasons)}\n"
            "推奨アクション: 上位オペレーターに転送してください。"
        )
    else:
        return "✅ エスカレーション不要 — 通常対応を継続してください。"


# =============================================================================
# エージェント & サーバー起動
# =============================================================================

AGENT_INSTRUCTIONS = """あなたは Zava 社のカスタマーサポートエージェント「Agent X」です。

## 役割
顧客からの問い合わせに対して、以下のツールを使って正確かつ迅速に対応します:

1. **search_order_history** — 顧客の注文履歴を検索
2. **search_faq** — FAQ から回答を検索
3. **check_escalation_needed** — エスカレーション判定
4. **Microsoft Learn MCP** — 技術的な質問への回答 (Microsoft 公式ドキュメント検索)

## 対応フロー
1. 顧客の問い合わせ内容を正確に理解する
2. 注文関連 → search_order_history を使用
3. 一般的な質問 → search_faq を使用
4. 技術的な質問・製品仕様 → Microsoft Learn MCP ツールを使用
5. 問題が複雑/顧客が不満 → check_escalation_needed で判定
6. 回答は簡潔かつ丁寧に、日本語で行う

## 制約
- 確認できない情報は推測しない
- 個人情報の取り扱いに注意する
- エスカレーション推奨の場合はその旨を顧客に伝える
"""


def main():
    """Agent X のエントリーポイント"""
    # ローカル実行時: AZURE_TENANT_ID を設定して正しいテナントを指定
    # Hosted Agent 上では DefaultAzureCredential() のみで OK
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    credential = AzureCliCredential(tenant_id=tenant_id) if tenant_id else DefaultAzureCredential()

    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        credential=credential,
    )

    # ローカルツール
    tools = [search_order_history, search_faq, check_escalation_needed]

    # Microsoft Learn MCP サーバーを接続 (認証不要)
    # https://learn.microsoft.com/api/mcp で公開されている MCP サーバー
    # ドキュメント検索・コードサンプル検索が利用可能
    microsoft_learn_mcp = client.get_mcp_tool(
        name="MicrosoftLearn",
        url="https://learn.microsoft.com/api/mcp",
        headers={},
        approval_mode="never_require",
    )
    tools.append(microsoft_learn_mcp)
    logger.info("Microsoft Learn MCP tool registered")

    agent = Agent(
        client=client,
        instructions=AGENT_INSTRUCTIONS,
        tools=tools,
        # Hosted Agent ではホスティング基盤が会話履歴を管理する
        default_options={"store": False},
    )

    # Responses プロトコルで HTTP サーバーを起動 (port 8088)
    server = ResponsesHostServer(agent)
    print("🚀 Agent X starting on http://localhost:8088")
    print("   POST /responses でリクエストを送信してください")
    print("   Microsoft Learn MCP: 有効")
    server.run()


if __name__ == "__main__":
    main()
