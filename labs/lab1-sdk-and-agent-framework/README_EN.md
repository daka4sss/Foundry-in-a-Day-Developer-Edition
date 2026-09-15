# Lab 1: Build Agents with Foundry SDK & Microsoft Agent Framework

**English** | [日本語](README.md)

> In this lab, you will use the Foundry SDK and CLI to create a Prompt Agent, then build and invoke **Agent X** with tools using Microsoft Agent Framework (MAF).

See the [root README](../../README_EN.md) for the setup instructions and overall exercise flow.

---

> ⚠️ **Shell environment**: The command examples in this workshop assume a **PowerShell** environment.  
> If you use macOS or Linux (bash, zsh, and so on), adapt variable declarations (`$VAR=...` → `VAR=...`) and line continuations (`` ` `` → `\`) for your environment.

## 🎯 Goals

- Create Foundry resources (AI Services, a project, and a model deployment) with Azure CLI (`az`)
- Create a **Prompt Agent** using the Foundry SDK (`azure-ai-projects`)
- Build **Agent X** using Microsoft Agent Framework (MAF)
- Implement custom tools for Zava customer support in Agent X
- Understand how to invoke a Foundry Agent from MAF

## 📋 Prerequisites

| Item | Requirement | How to Check |
|------|------|---------|
| Python | 3.11 or later | `python --version` |
| Azure CLI | 2.60 or later | `az version` |
| VS Code | Python extension installed | Check the Extensions panel |
| Azure subscription | An active subscription | `az account show` |
| Azure CLI sign-in | Signed in to the correct tenant | See below |

### Verify Your Azure CLI Sign-In

```powershell
# Check the current sign-in
az account show --query "{name:name, tenantId:tenantId}" -o table

# If you are not signed in or are using the wrong tenant:
az login --tenant <YOUR-TENANT-ID>
```

> ⚠️ **How to find your tenant ID**: Azure portal → Microsoft Entra ID → Overview → Tenant ID  
> Alternatively, list your tenants with `az account list --query "[].{Name:name, TenantId:tenantId}" -o table`.

## 🎬 Workshop Scenario

In this workshop, you will automate customer support for **Zava**, a fictional e-commerce company, using AI agents.

| Item | Details |
|------|------|
| Company | Zava — a fictional e-commerce site that sells earbuds, smartwatches, and other products |
| Challenge | Customer support inquiries have increased beyond what staff can handle manually |
| Solution | AI agents automate order history searches, FAQ responses, and escalation decisions |
| Architecture | An agent architecture centered on Agent X (a specialist agent) |

> 💡 Zava is a fictional company created for this workshop and is not associated with any real service.

---

## Exercise 0: Create Foundry Resources with Azure CLI (15 min)

In this exercise, you will use Azure CLI to create the Foundry resources required for the hands-on lab.

### 0.1 Set Variables

```powershell
# ---- Change these values as desired ----
$RESOURCE_GROUP = "rg-foundry-workshop"
$LOCATION = "eastus2"
$AI_SERVICES_NAME = "ai-foundry-workshop-$(Get-Random -Maximum 9999)"  # Name must be globally unique
$PROJECT_NAME = "zava-support"
$MODEL_DEPLOYMENT_NAME = "gpt-4.1-mini"
```

> ⚠️ `$AI_SERVICES_NAME` must be globally unique. `Get-Random` generates a suffix automatically, but rerun the command if the generated name is already in use.

### 0.2 Create the Resource Group

```powershell
az group create --name $RESOURCE_GROUP --location $LOCATION
```

### 0.3 Create the Foundry Resource and Project in the Azure Portal

Because the `az ai` extension is currently unavailable, create the Foundry resource (AI Services) and project together in the **Azure portal**.

#### Steps

1. Open the [Azure portal](https://portal.azure.com/) in your browser.
2. Confirm that the **Directory** shown in the upper-right corner matches the tenant returned by `az account show`.
3. Enter `Foundry` in the **search bar** at the top of the page, then select **Microsoft Foundry** from the list of services.
4. Select **+ Create**.
5. Under **Instance details**, enter the following values:
   - **Subscription**: The subscription you will use
   - **Resource group**: `rg-foundry-workshop`, created in Exercise 0.2
   - **Region**: `East US 2` (matching `$LOCATION` from Exercise 0.1)
   - **Name (resource name)**: The value of `$AI_SERVICES_NAME` from Exercise 0.1 (for example, `ai-foundry-workshop-xxxx`) — this must be globally unique
6. In the **Project** section, select **Create a project** and enter **`zava-support`** (the value of `$PROJECT_NAME` from Exercise 0.1) as the project name. This creates the Foundry resource and project together.
7. Select **Review + create**, then **Create**, and wait for provisioning to complete (2–3 minutes).

![Example values](docs/images/Foundry%20Creation.png)

**✅ Verification:**
- After deployment completes, select **Go to resource** and confirm that the Microsoft Foundry resource overview page opens.
- From the **Open in Microsoft Foundry portal** link at the top of the overview page, confirm that you can open the `zava-support` project.
- Confirm that the project's Overview displays the **Microsoft Foundry project endpoint** (`https://<account>.services.ai.azure.com/api/projects/<project>`).

> ⚠️ Save this **Project endpoint** because you will use it in Exercises 0.5 and 1.3.

### 0.4 Deploy the Model from the Microsoft Foundry Portal

Deploy the `gpt-4.1-mini` model used in this workshop to the `zava-support` project created in Exercise 0.3.

#### Steps

1. Open the [Microsoft Foundry portal](https://ai.azure.com/) and select the `zava-support` project.
2. Select **Build** from the top menu, then open **Models** from the left navigation.
3. Select **Deploy a base model**.
4. Select **`gpt-4.1-mini`** from the model list, then select **Confirm**.
5. Select **Deploy**, keep the default settings in the dialog, and start the deployment.

![How to deploy the model](docs/images/GPT-4.1-mini.png)

**✅ Verification:**
- The deployment list shows `gpt-4.1-mini` with a **Succeeded** status.
- The deployment name matches the value of `$MODEL_DEPLOYMENT_NAME` from Exercise 0.1.

### 0.5 Find the Endpoint and Tenant ID

#### Get the Project Endpoint from the Foundry Portal

> 💡 If you saved the **Project endpoint** when provisioning completed in Exercise 0.3, you can skip this procedure.  
> If you did not save it, retrieve it using the following steps.

1. Open the `zava-support` project in the new [Microsoft Foundry portal](https://ai.azure.com/) UI.
2. Open the project's **Home** page.
3. Select the copy button to the right of **Project endpoint** to copy the value.
   - Format: `https://<account>.services.ai.azure.com/api/projects/<project>`

![Project endpoint](docs/images/project-endpoint.png)

Save the copied value in a text editor or another temporary location. In Exercise 1.3, you will paste it into `FOUNDRY_PROJECT_ENDPOINT` in `.env`.

#### Get the Tenant ID

Run the following command to find your current tenant ID. Save the returned value so you can paste it into `AZURE_TENANT_ID` in `.env` during Exercise 1.3.

```powershell
az account show --query tenantId -o tsv
```

> 💡 The application reads values from `.env`, so you do not need to set a PowerShell environment variable here. Once you have the value, continue to the next exercise.

---

## Exercise 1: Create an Agent with the Foundry SDK (20 min)

> ❗ **Prerequisite**: Complete Exercise 0 and make sure you have the project endpoint and tenant ID.

### 1.1 Set Up the Environment

Run the following commands from the repository root directory (`Foundry-in-a-day-3/`):

```powershell
cd labs/lab1-sdk-and-agent-framework
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

> ⚠️ `pip install` may take 1–2 minutes to complete. If an error occurs, check your Python version.

### 1.3 Configure Environment Variables

Copy `.env.example` to create `.env`, then configure its values.

```powershell
Copy-Item .env.example .env
```

Open `.env` in VS Code and edit it:

```env
# Endpoint obtained in Exercise 0.5
FOUNDRY_PROJECT_ENDPOINT="https://<YOUR-RESOURCE-NAME>.services.ai.azure.com/api/projects/<YOUR-PROJECT-NAME>"

# Leave unchanged (the model name deployed in Exercise 0.4)
AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1-mini"

# Leave unchanged
MICROSOFT_FOUNDRY_AGENT_NAME="zava-support-agent-x"

# Tenant ID obtained in Exercise 0.5
AZURE_TENANT_ID="<YOUR-TENANT-ID>"
```

> ⚠️ **Common mistake**: Do not add `/` to the end of the endpoint.  
> 💡 **What happens if the tenant ID is not set?**: The authentication token tenant will not match, causing a  
> `Token tenant ... does not match resource tenant` error.

### 1.4 Create the Prompt Agent with the SDK

Run `src/agent_x/create_agent.py` to create a Prompt Agent in Foundry.

```powershell
python src/agent_x/create_agent.py
```

**✅ Expected output:**
```
✅ Agent created successfully!
   Name:    zava-support-agent-x
   ID:      zava-support-agent-x:1
   Version: 1
   Model:   gpt-4.1-mini

💡 次のステップ: chat_with_agent.py でエージェントと対話してみましょう
```

**Key points:**
- `AIProjectClient` — Client used to connect to the Foundry project
- `AzureCliCredential(tenant_id=...)` — Authenticates using the token from `az login`
- `PromptAgentDefinition` — Configures the agent definition, including the model and instructions
- `project.agents.create_version()` — Creates a versioned agent

### 1.5 Test a Conversation with the Agent Using the SDK

Send messages to the agent you created through the SDK.

```powershell
python src/agent_x/chat_with_agent.py
```

**✅ Example expected output:**
```
🔗 Conversation started (ID: conv_xxxxx...)
🤖 Agent: zava-support-agent-x
--------------------------------------------------

📤 User: 顧客ID C001 の最近の注文について教えてください
📥 Agent: かしこまりました。顧客ID C001様の最近のご注文内容を確認いたします...

📤 User: その注文のステータスを確認してもらえますか？
📥 Agent: 承知いたしました。...

📤 User: 返品ポリシーについて教えてください
📥 Agent: 返品ポリシーについてご案内いたします。...

--------------------------------------------------
✅ マルチターン会話のテスト完了!
```

**Key points:**
- `project.get_openai_client()` — Gets an OpenAI-compatible client
- `openai.conversations.create()` — Starts a multi-turn conversation and manages its state with a conversation ID
- `openai.responses.create(conversation=..., input=...)` — Sends a message using the conversation ID
- `extra_body={"agent_reference": ...}` — Identifies the agent to invoke by name

> 💡 **Why OpenAI-compatible?** Foundry provides an interface compatible with the OpenAI API.  
> This lowers the learning curve because you can apply your existing knowledge of the OpenAI SDK.

---

## Exercise 2: Build Agent X with MAF (20 min)

### 2.1 Agent X Overview

Agent X is a **specialist agent for Zava customer support**. It has the following tools:

| Tool | Description | Example Use |
|--------|------|-----------|
| `search_order_history` | Searches a customer's order history | "What is the status of my order?" |
| `search_faq` | Searches the FAQ database for an answer | "What is the return policy?" |
| `check_escalation_needed` | Determines whether escalation is required | "The product is defective! Give me a refund!" |

> 💡 **What is MAF?** Microsoft Agent Framework is a framework for building and hosting agents.  
> It combines tool definitions, an LLM client, and instructions in a single Agent object that can be exposed as an HTTP server.

### 2.2 Code Walkthrough: main.py

Open `src/agent_x/main.py` in VS Code and review its structure.

```python
from agent_framework import Agent, tool          # MAF core
from agent_framework.foundry import FoundryChatClient  # Foundry connection
from agent_framework_foundry_hosting import ResponsesHostServer  # HTTP server
```

**Key components:**

| Component | Role |
|----------------|------|
| `FoundryChatClient` | Client that connects to the model in the Foundry project |
| `@tool` decorator | Registers a Python function as a tool that the LLM can invoke |
| `Agent` | Agent definition that combines tools, instructions, and a client |
| `ResponsesHostServer` | Starts an HTTP server using the Responses protocol (port 8088) |

### 2.3 Implement the Tools

Each tool is defined using the `@tool` decorator:

```python
@tool(approval_mode="never_require")
def search_order_history(
    customer_id: Annotated[str, Field(description="顧客ID")],
) -> str:
    """顧客の注文履歴を検索します。"""
    # 実装...
```

**Key points for tool definitions:**
- `@tool(approval_mode="never_require")` — Runs automatically without human approval
- `Annotated[str, Field(description="...")]` — Provides the LLM with a description of the argument
- Docstring — Description the LLM uses when selecting a tool

> 💡 **Hands-on task**: Review the tool section in `src/agent_x/main.py` and try implementing an additional tool.

### 2.4 Run and Test Locally

Start the server in **Terminal 1**:

```powershell
python src/agent_x/main.py
```

**✅ Expected output:**
```
🚀 Agent X starting on http://localhost:8088
   POST /responses でリクエストを送信してください
   Microsoft Learn MCP: 有効
YYYY-MM-DD ... INFO __main__: Microsoft Learn MCP tool registered
YYYY-MM-DD ... INFO hypercorn.error: Running on http://0.0.0.0:8088 (CTRL + C to quit)
```

> 💡 The server is ready when `Running on http://0.0.0.0:8088` appears.  
> The terminal remains blocked while the server is running, so open **another terminal** for testing.

In **Terminal 2** (a new terminal), send a request:

> 💡 The following command is long, but you can copy and paste it as-is.

```powershell
# Test an order history search
$body = '{"input": "顧客ID: C001 の注文履歴を教えて", "model": "gpt-4.1-mini"}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
(Invoke-WebRequest -Uri http://localhost:8088/responses -Method POST -ContentType "application/json" -Body $bytes -TimeoutSec 60).Content | ConvertFrom-Json | ConvertTo-Json -Depth 5
```

> 💡 When sending JSON that contains Japanese text, convert it with `[System.Text.Encoding]::UTF8.GetBytes()`.  
> Without this conversion, the text may become garbled and prevent the agent from responding correctly.

**✅ Expected output (excerpt):**
```json
{
  "status": "completed",
  "output": [
    { "type": "function_call", "name": "search_order_history", ... },
    { "type": "function_call_output", ... },
    { "type": "message", "content": [{ "text": "顧客ID C001 の注文履歴は..." }] }
  ]
}
```

> 💡 A `status` value of `"completed"` indicates success. If it is `"failed"`, refer to the troubleshooting section.

## Exercise 3: Invoke a Foundry Agent from MAF (10 min)

### 3.1 Invoke a Foundry Agent from MAF with `FoundryAgent`

MAF (`agent_framework_foundry`) provides a class that lets you **reference and invoke a Prompt or Hosted Agent registered in Foundry directly by name**:

```python
from agent_framework_foundry import FoundryAgent
from azure.identity.aio import AzureCliCredential

async with AzureCliCredential(tenant_id=TENANT_ID) as credential:
    agent = FoundryAgent(
        project_endpoint=PROJECT_ENDPOINT,
        agent_name="zava-support-agent-x",   # Prompt Agent created in Exercise 1.4
        credential=credential,
    )

    session = agent.create_session()          # Session for multi-turn conversations
    result = await agent.run("顧客ID C001 の最近の注文を教えてください", session=session)
    print(result.text)
```

**Key points:**
- `FoundryAgent` automatically adds an **`agent_reference`**, the mechanism used to invoke a Foundry-registered agent by name
- The caller only needs the **agent name** and does not need to know which model or tools the agent uses
- To add local tools, pass `tools=[...]` to combine a Foundry Prompt Agent with local tools
- `agent_version` can be omitted for a Hosted Agent; a Prompt Agent normally specifies `agent_version` (when omitted, the latest version is used)

### 3.2 Demo: Invoke the Agent

Run `src/agent_x/chat_with_agent_maf.py`:

```powershell
python src/agent_x/chat_with_agent_maf.py
```

**✅ Example expected output:**
```
============================================================
MAF FoundryAgent → Foundry Prompt Agent (zava-support-agent-x)
============================================================

--- ターン 1 ---
📤 User : 顧客ID C001 の最近の注文を教えてください
📥 Agent: ご連絡ありがとうございます。顧客ID C001様の直近のご注文は...

--- ターン 2 ---
📤 User : その注文がまだ届いていないようなのですが、ステータスを確認できますか？
📥 Agent: 配送業者のシステム上では、注文は…配達完了と記録されております...

--- ターン 3 ---
📤 User : 返品ポリシーについても教えてください
📥 Agent: 当社の返品ポリシーは以下の通りです...

============================================================
✅ 全ターン完了
```

> 💡 Because the same session (`agent.create_session()`) is shared, the context from the previous turn is retained when Turn 2 refers to "that order."

> ⚠️ **Note**: The Prompt Agent created in Exercise 1.4 has no tools. If you ask it about order history, it returns model-generated content without searching actual data. To use actual data, deploy the locally hosted Agent X with tools from Exercise 2 to Foundry (covered in Lab 2), then change `MICROSOFT_FOUNDRY_AGENT_NAME` to that agent.

---

## 📝 Summary

| What You Did | Technology Used |
|------------|-----------|
| Created Foundry resources | Azure CLI (`az`) |
| Created a Prompt Agent | `azure-ai-projects` SDK |
| Built Agent X | Microsoft Agent Framework (MAF) |
| Implemented tools | `@tool` decorator |
| Tested locally | `ResponsesHostServer` (port 8088) |
| Integrated agents | Invocation using `agent_reference` |

## 🔗 References

- [Foundry Samples (GitHub)](https://github.com/microsoft-foundry/foundry-samples)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Foundry Hosted Agents documentation](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents)
- [Agent Framework Quick Start](https://learn.microsoft.com/agent-framework/tutorials/quick-start)

---

## 🚨 Troubleshooting

### Error: `Token tenant ... does not match resource tenant`

**Cause**: `AZURE_TENANT_ID` is not set in `.env`, or the `az login` tenant differs from the resource tenant.

**Resolution**:
```powershell
# Check the correct tenant ID
az account show --query tenantId -o tsv

# Set it in .env
# AZURE_TENANT_ID="<value-from-above>"

# Sign in to the correct tenant again if necessary
az login --tenant <YOUR-TENANT-ID> --scope "https://ai.azure.com/.default"
```

### Error: `Invoke-WebRequest` Times Out

**Cause**: The server is not running, or port 8088 is already in use.

**Resolution**:
```powershell
# Check whether the server is running
Get-NetTCPConnection -LocalPort 8088 -ErrorAction SilentlyContinue

# Stop the process if the port is in use
Get-NetTCPConnection -LocalPort 8088 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }

# Restart the server
python src/agent_x/main.py
```

### Error: `'ai' is misspelled or not recognized by the system.` from `az ai project create`

**Cause**: As of May 2026, the `az ai` extension is unavailable and cannot be dynamically installed. Running `az config set extension.dynamic_install_allow_preview=true` does not resolve the issue.

**Resolution**: Create the Foundry resource and project from the [Microsoft Foundry portal](https://ai.azure.com/) instead of the CLI. See [Exercise 0.3](#03-create-the-foundry-resource-and-project-in-the-azure-portal) for instructions.

### Error: `ModuleNotFoundError: No module named 'agent_framework'`

**Cause**: The virtual environment is not activated.

**Resolution**:
```powershell
# Activate the virtual environment
.venv\Scripts\activate

# Check whether the package is installed
pip list | Select-String "agent-framework"
```

### Requests Do Not Respond for a Long Time (Hang)

**Cause**: The required patch has probably not been applied.

**Resolution**:
1. Press Ctrl+C to stop the server.
2. Run `python scripts/patch_responses.py`.
3. Restart the server with `python src/agent_x/main.py`.

### Error: `AuthorizationFailed` / `does not have authorization to perform action`

**Cause**: The required RBAC role has not been assigned.

**Resolution**:
```powershell
# Check your current role assignments
az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --query "[].{Role:roleDefinitionName, Scope:scope}" -o table
```

Required roles:
- Resource creation (Exercise 0): `Contributor` on the subscription or resource group
- Agent creation and use (Exercises 1–3): `Azure AI Developer` on the AI Services resource

Ask an administrator to run the following command:
```powershell
# Run by an administrator: Assign the Azure AI Developer role
az role assignment create `
  --assignee <YOUR-USER-OBJECT-ID> `
  --role "Azure AI Developer" `
  --scope /subscriptions/<SUB-ID>/resourceGroups/<RG>/providers/Microsoft.CognitiveServices/accounts/<AI-SERVICES-NAME>
```

### Error: `Forbidden` / `Principal does not have access to API/Operation`

**Cause**: The `Azure AI Developer` role is not assigned on the AI Services resource (for example, it is assigned only on the project).

**Resolution**: Check the role assignment scope. The role must be assigned on the AI Services resource (the parent resource).
```powershell
# Assign the role on the AI Services resource itself, not the project
$AI_RESOURCE_ID = az cognitiveservices account show --name <AI_SERVICES_NAME> --resource-group <RESOURCE_GROUP> --query id -o tsv
az role assignment create --assignee $(az ad signed-in-user show --query id -o tsv) --role "Azure AI Developer" --scope $AI_RESOURCE_ID
```
