#!/usr/bin/env bash
# Sync values from .env into the current azd environment.
# Usage:
#   ./scripts/sync-azd-env-from-dotenv.sh
#   ./scripts/sync-azd-env-from-dotenv.sh ./path/to/.env

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="${1:-$REPO_ROOT/.env}"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: .env が見つかりません: $ENV_FILE" >&2
    echo ".env.example をコピーして値を編集してください。" >&2
    exit 1
fi

if ! command -v azd >/dev/null 2>&1; then
    echo "ERROR: azd コマンドが見つかりません。Azure Developer CLI をインストールしてください。" >&2
    exit 1
fi

echo "Reading $ENV_FILE ..."
count=0
while IFS= read -r raw_line || [[ -n "$raw_line" ]]; do
    # 前後空白除去
    # Remove surrounding whitespace
    line="${raw_line#"${raw_line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"

    [[ -z "$line" ]] && continue
    [[ "$line" == \#* ]] && continue
    [[ "$line" != *=* ]] && continue

    key="${line%%=*}"
    val="${line#*=}"
    # キー側の trailing space を除去
    # Remove trailing whitespace from the key
    key="${key%"${key##*[![:space:]]}"}"
    # 値側の leading space を除去
    # Remove leading whitespace from the value
    val="${val#"${val%%[![:space:]]*}"}"

    # 前後の引用符を除去
    # Remove surrounding quotation marks
    if [[ ( "$val" == \"*\" && "$val" == *\" ) || ( "$val" == \'*\' && "$val" == *\' ) ]]; then
        val="${val:1:${#val}-2}"
    fi

    if [[ -z "$val" ]]; then
        echo "WARN: 値が空のためスキップ: $key" >&2
        continue
    fi

    echo "azd env set $key ***"
    azd env set "$key" "$val"
    count=$((count + 1))
done < "$ENV_FILE"

echo
echo "Done. $count 個の環境変数を azd 環境に登録しました。"
