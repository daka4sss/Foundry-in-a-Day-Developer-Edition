# 事前準備 (Setup)

[English](setup_EN.md) | **日本語**

このワークショップを始める前に、以下の手順で環境を準備してください。
**所要時間: 約 30 分**

> ⚠️ ワークショップ当日の会場 Wi-Fi では大きなダウンロードに時間がかかる場合があります。
> 必ず **事前に** 完了させてください。

---

## ✅ 事前準備チェックリスト

- [ ] [1. アカウント・権限の確認](#1-アカウント権限の確認)
- [ ] [2. ツールのインストール](#2-ツールのインストール)
- [ ] [3. VS Code の準備](#3-vs-code-の準備)
- [ ] [4. リポジトリの取得と環境変数](#4-リポジトリの取得と環境変数)
- [ ] [5. 動作確認](#5-動作確認)

---

## 1. アカウント・権限の確認

### 1.1 Azure サブスクリプション

- 有効な Azure サブスクリプションを保有していること
- ロール: **Contributor** 以上 (Hosted Agent デプロイには **Owner** または **User Access Administrator** 推奨)
- リージョン: **North Central US** (Hosted Agent の現状の制約)

- 5/18 のワークショップでは Microsoft が提供する環境での作業も可能です。本環境へのサインイン情報と手順については部屋で共有している別PPT資料をご参照ください。

### 1.2 GitHub アカウント (任意)

- 本リポジトリを fork / clone するため

---

## 2. ツールのインストール

### 2.1 Python 3.11+

- 公式: https://www.python.org/downloads/

```powershell
# PowerShell (Windows)
python --version    # 3.11 以上が表示されること
# 表示されない場合は py コマンドを試す
py --version
```

```bash
# Bash (macOS / Linux)
python3 --version
```

### 2.2 uv (Python パッケージマネージャ)

```powershell
# PowerShell
pip install uv
```

```bash
# Bash
pip install uv
# または
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.3 Azure CLI (`az`)

- 公式: https://learn.microsoft.com/cli/azure/install-azure-cli

```powershell
# PowerShell (Windows) — winget 利用可
winget install -e --id Microsoft.AzureCLI
```

```bash
# Bash (macOS)
brew install azure-cli
```

### 2.4 Azure Developer CLI (`azd`)

- 公式: https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd

```powershell
# PowerShell (Windows)
winget install Microsoft.Azd
```

```bash
# Bash (macOS)
brew tap azure/azd && brew install azd
```

`azd` の AI Agent 拡張も必要です:

```bash
azd ext install azure.ai.agents
```

---

## 3. VS Code の準備

### 3.1 Visual Studio Code 本体

- 公式: https://code.visualstudio.com/download

### 3.2 推奨拡張機能

| 拡張 | 用途 |
|---|---|
| Python (`ms-python.python`) | Python 開発 |
| Azure Tools (`ms-vscode.vscode-node-azure-pack`) | Azure リソース操作 |
| Microsoft 365 Agents Toolkit | Agent サンプルのスキャフォールド |

VS Code で `Ctrl + Shift + X` (macOS: `Cmd + Shift + X`) → 名前で検索してインストール。

---

## 4. リポジトリの取得と環境変数

### 4.1 リポジトリの取得

```bash
git clone https://github.com/<your-org>/Foundry-in-a-Day-Developer-Edition.git
cd Foundry-in-a-Day-Developer-Edition
```

### 4.2 環境変数ファイルの作成

```powershell
# PowerShell
Copy-Item .env.example .env
```

```bash
# Bash
cp .env.example .env
```

`.env` を開いて、自分の Foundry プロジェクトの値に書き換えてください。

> 🔒 `.env` は `.gitignore` 済みです。**絶対に secret をコミットしないでください。**

### 4.3 仮想環境のセットアップ

```bash
uv venv
# PowerShell
.venv\Scripts\Activate.ps1
# Bash
source .venv/bin/activate

uv pip install -e .
```

---

## 5. 動作確認

すべて成功すれば準備完了です。

```bash
python --version            # 3.11 以上
uv --version                # 任意のバージョン
az --version                # 2.80 以上推奨
azd version                 # 1.24.0 以上推奨
azd ext list                # ai.agents が含まれること
```

Azure へのサインイン:

```bash
az login
azd auth login
```

---

## 🆘 うまくいかないとき

- 環境構築のトラブル: [troubleshooting.md](troubleshooting.md) を参照
- 当日: 会場スタッフ・TA に声がけ

---

## 💡 OS 差分のメモ

- **Windows**: `python` が PATH にない場合は `py -3.11` を使用
- **Windows**: 改行コード設定 — `git config --global core.autocrlf input` 推奨
- **macOS**: システム Python ではなく Homebrew / pyenv 経由の Python を使うこと
- **社内 Proxy 環境**: `pip` / `uv` / `az` それぞれに Proxy 設定が必要 ([troubleshooting.md](troubleshooting.md) 参照)
