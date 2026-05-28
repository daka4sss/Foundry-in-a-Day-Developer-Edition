# Troubleshooting

ワークショップで起きやすいトラブルと対応方法をまとめます。
新しい問題に遭遇したら、TA / 講師に共有のうえこのファイルに追記してください。

> 💡 まずは Lab の **「よくあるエラー」** セクションを確認 → 解決しなければここを参照。

---

## 目次

- [Azure 認証](#azure-認証)
- [リージョン / クォータ制約](#リージョン--クォータ制約)
- [ネットワーク / Proxy](#ネットワーク--proxy)
- [Python / uv インストール](#python--uv-インストール)
- [VS Code 拡張](#vs-code-拡張)
- [文字化け / 改行コード](#文字化け--改行コード)

---

## Azure 認証

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| `DefaultAzureCredential` が失敗 | `az` または `azd` の認証セッション切れ | `az login` / `azd auth login` を再実行 | Lab 1〜3 |
| `AuthenticationError` | テナント / サブスクリプションの不一致 | `az account set --subscription <id>` で切替 | Lab 1〜3 |
| | | | |

---

## リージョン / クォータ制約

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| Hosted Agent デプロイで region エラー | Hosted Agent は **North Central US** のみ対応 (執筆時点) | `azd init` 時に `--location northcentralus` を指定 | Lab 2 |
| `429 Too Many Requests` | モデルのレート制限 | しばらく待つ / モデルクォータを確認 | Lab 1〜3 |
| `DeploymentNotFound` | モデルデプロイ名の不一致 | Foundry ポータル **Build → Deployments** で確認し `.env` を修正 | Lab 1〜3 |
| | | | |

---

## ネットワーク / Proxy

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| `pip` / `uv` install がタイムアウト | 社内 Proxy 未設定 | `HTTP_PROXY` / `HTTPS_PROXY` 環境変数を設定 | setup |
| `az login` がブラウザを開かない | 社内 Proxy / SSO 制約 | `az login --use-device-code` を試す | setup |
| | | | |

---

## Python / uv インストール

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| `python: command not found` (Windows) | PATH 未設定 | `py -3.11` を使うか PATH を追加 | setup |
| `uv pip install` が SSL エラー | 社内証明書 | `REQUESTS_CA_BUNDLE` に社内 CA を指定 | setup |
| `.venv/script/activate` でスクリプト実行が無効 | Execution Policy | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force` を実行 | setup |
| | | | |

---

## VS Code 拡張

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| Microsoft 365 Agents Toolkit でサンプルが見えない | 拡張バージョンが古い | 最新版に更新 → VS Code を再起動 | Lab 1 |
| | | | |

---

## 文字化け / 改行コード

| 症状 | 想定原因 | 解決方法 | 出やすい Lab |
|---|---|---|---|
| ターミナル日本語が文字化け (Windows) | コードページ不一致 | `chcp 65001` で UTF-8 に切替 | 全般 |
| `git diff` で改行が大量に変更扱い | 改行コード CRLF/LF 混在 | `git config --global core.autocrlf input` | 全般 |
| | | | |

---

## それでも解決しない場合

- 会場スタッフ / TA に声がけ
- リポジトリの Issue を立てる (タイトルに `[lab1]` などラベル)
