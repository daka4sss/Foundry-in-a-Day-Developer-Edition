# Foundry in a Day — Developer Edition

[English](README_EN.md) | **日本語**

> **最先端の エージェント 開発を半日で体験！** 先着 30 名様限定

Microsoft の AI エージェント 開発・運用プラットフォーム **Microsoft Foundry** を半日で体験できるワークショップを開催します。エージェント開発を効率化されたい方はぜひご参加をご検討くださいませ。

また、ワークショップで利用する **Azure 環境は Microsoft がご用意** いたします。

---

## 📅 開催情報

| 項目 | 内容 |
|---|---|
| **日時** | 2026 年 5 月 18 日 (月) 14:00 〜 18:00 (開場 13:30) |
| **会場** | 日本マイクロソフト株式会社 品川本社 31 階 セミナールーム B |
| **講師** | Microsoft Global Black Belt |
| **定員** | 30 名 (先着) |

---

## 🎯 ゴール

このワークショップを終えると、参加者は次のことができるようになります:

- [ ] Microsoft Foundry の概念と最新動向を説明できる
- [ ] SDK / CLI を使って Agent を新規作成できる
- [ ] Microsoft Agent Framework で Agent を実装できる
- [ ] Hosted Agent として Foundry にデプロイできる
- [ ] 作成した Agent を評価 (Evaluation) できる

---

## 👥 対象者

- 普段の業務で **エージェント開発をされている方**
- **これからエージェント開発をする予定** の方
- 下記「[ご参加にあたって](#-ご参加にあたって)」の条件を満たす環境をご用意いただける方

> ⚠️ **コードを使ったエージェント開発を集中的に実施します。予めご了承ください。**
> GUI でのエージェント開発をご希望される場合は、GUI での開発や管理をメインとした別コンテンツにて個別開催いたしますので、担当営業までご相談ください。

---

## 📅 アジェンダ

| 時刻 | セッション |
|---|---|
| 14:00 - 14:20 | Microsoft Foundry 最新情報 |
| 14:20 - 15:30 | SDK / CLI で開発するエージェント |
| 15:30 - 16:40 | Hosted Agent へのデプロイ  |
| 16:40 - 18:00 | 作ったエージェントの評価 |

> ※ プログラムの内容はやむを得ず変更する場合がございます。あらかじめご了承ください。

---

## ✅ ご参加にあたって

下記の条件を満たす環境を **事前に** ご用意ください。詳しいセットアップ手順は **[setup.md](setup.md)** を参照してください。

- [ ] **Web に接続でき、Azure Portal にアクセスできる PC** を持参できること
  - プロキシ経由など、社用 PC の設定によって弊社ネットワークに接続できない可能性がございます。予めご了承ください。
- [ ] **Visual Studio Code** をインストールしていること
- [ ] **Python 環境** があること (Python 3.10 〜 3.13 をサポートしています)
- [ ] **VSCode Extension** で **REST Client Extension** のインストールができること
- [ ] スマートフォンに **"Microsoft Authenticator"** をインストールできること
- [ ] **Git CLI で Clone** が利用できること
  - 初めての方は事前に [こちら](https://learn.microsoft.com/training/paths/intro-to-vc-git/) を受講ください
- [ ] **GitHub Account** があると好ましい

---

## 🧪 Lab 一覧

| # | タイトル | 所要 |
|---|---|---|
| 1 | [Build Agents with Foundry SDK & Microsoft Agent Framework](labs/lab1-sdk-and-agent-framework/README.md) | 〜105分 |
| 2 | [Hosted Agent へのデプロイ](labs/lab2-hosted-agent-deploy/README.md) | 〜45分 |
| 3 | [作ったエージェントの評価](labs/lab3-evaluation/README.md) | 〜45分 |

詳細は **[labs/README.md](labs/README.md)** を参照してください。

## 🏁 完了条件

- [ ] Lab 1 〜 3 をすべて完走
- [ ] 自分の Hosted Agent が Foundry ポータルから呼び出せる
- [ ] 評価結果がポータルに表示される

---

## 🆘 困ったとき

| 状況 | 参照先 |
|---|---|
| 環境構築でつまずいた | [setup.md](setup.md) |
| Lab 進行中にエラー | [troubleshooting.md](troubleshooting.md) |
| 当日の質問 | 会場スタッフ・TA へお声がけください |

---

## 📜 行動規範

本ワークショップは **Microsoft イベント行動規範** に従って運営されます。
詳細は [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) を参照してください。

---

## 👨‍🏫 講師・TA の方へ

講師向けメモは **[instructor/](instructor/)** ディレクトリにあります。
