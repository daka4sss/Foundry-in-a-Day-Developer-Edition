# Microsoft Foundry Hosted Agent 用コンテナ (linux/amd64)
# Container for a Microsoft Foundry Hosted Agent (linux/amd64)
FROM python:3.12-slim

WORKDIR /app

# 依存先にインストール (キャッシュ効率向上)
# Install dependencies first for better layer caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# アプリ本体をコピー
# Copy the application
COPY . /app

# Foundry Hosted Agent はポート 8088 で待ち受ける
# Foundry Hosted Agents listen on port 8088
EXPOSE 8088

CMD ["python", "main.py"]
