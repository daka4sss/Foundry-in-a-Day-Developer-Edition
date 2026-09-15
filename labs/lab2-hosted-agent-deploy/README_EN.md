# Lab 2: Deploy a Hosted Agent

**English** | [日本語](README.md)

> In this hands-on lab, you will use the **Agent Skills** feature in Microsoft Agent Framework v1.0 or later to build an **orchestration agent** that routes requests between two agents registered in Microsoft Foundry, then deploy it as a **Foundry Hosted Agent**.

## Architecture

```
                           ┌────────────────────────────────────────┐
   User ──▶ Orchestrator ─▶│ ms_learn_agent (Microsoft technology)  │
            (this repo)    │ web_search_agent (Web search)          │
                           └────────────────────────────────────────┘
            ▲ Routing decisions are defined in
              skills/orchestrator-routing/SKILL.md, not instructions
```

| Role | Implementation |
| --- | --- |
| Orchestration agent | The `Agent` in this repository (Foundry LLM + Agent Skills) |
| Microsoft technology expert agent | An existing Prompt Agent registered in Foundry (based on Microsoft Learn) |
| Web search agent | An existing Prompt Agent registered in Foundry (Bing grounding, and so on) |
| Routing control | [`skills/orchestrator-routing/SKILL.md`](agent-src/skills/orchestrator-routing/SKILL_EN.md) (English reference for the Agent Skill) |

## Prerequisites

- A [Microsoft Foundry project](https://learn.microsoft.com/en-us/azure/foundry/how-to/create-projects) and an LLM model deployment (for example, `gpt-5.2`; the deployment name can be anything)
- You will create two subagents in the Foundry project (Microsoft technology expert and Web search) by running the script in [Step 3](#step-3-create-the-subagents)
- Python 3.10+
- [Azure CLI 2.80+](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli), with `az login` completed
- [Azure Developer CLI (azd) 1.24.0+](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd), with the AI Agents extension and authentication completed: `azd ext install azure.ai.agents` / `azd auth login`
- Role: **Azure AI Project Manager** on the Foundry project (see [Step 0](#step-0-verify-and-assign-roles))

---

## Step 0. Verify and Assign Roles

When `azd deploy` creates a new Hosted Agent, the platform must assign the `Azure AI User` role to the agent identity it creates internally. The minimum role that can perform this assignment is **Azure AI Project Manager** at the project scope.  
The `Azure AI User` role alone does not include permission to assign roles, so creating a new Hosted Agent will fail.

> If you already have the **Azure AI Project Manager**, **Azure AI Account Owner**, or **Owner** role on the target Foundry project, skip this step.

### A. Check Your Current Assignment in the Azure Portal

1. Open the [Azure portal](https://portal.azure.com/).
2. Search for the **Foundry project** resource in the search bar (for example, filter by its display name or resource group).
3. In the left menu, select **Access control (IAM) → Role assignments → View my access**.
4. If the list includes any of the following roles, this step is complete:
   - `Azure AI Project Manager`
   - `Azure AI Account Owner`
   - `Owner`

### B. Assign the Role in the Azure Portal if You Do Not Have Permission

Ask an **Owner** or **User Access Administrator** of the subscription or project to assign the role, or follow these steps if you hold one of those roles:

1. Open **Access control (IAM)** for the Foundry project resource.
2. Select **+ Add → Add role assignment**.
3. Under **Role**, select `Azure AI Project Manager`, then select **Next**.
4. Under **Members**, find and add the target user (the workshop participant), then select **Next**.
5. Select **Review + assign**.

### C. Alternative: Assign the Role with Azure CLI

#### Windows (PowerShell)

```powershell
# Copy the project's ARM ID (Foundry portal → Project → JSON View)
$PROJECT_ID = "<your-foundry-project-arm-id>"
$USER_OBJECT_ID = (az ad signed-in-user show --query id -o tsv)

az role assignment create `
  --assignee-object-id $USER_OBJECT_ID `
  --assignee-principal-type User `
  --role "Azure AI Project Manager" `
  --scope $PROJECT_ID
```

#### Linux / macOS (bash)

```bash
# Copy the project's ARM ID (Foundry portal → Project → JSON View)
PROJECT_ID="<your-foundry-project-arm-id>"
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --assignee-object-id "$USER_OBJECT_ID" \
  --assignee-principal-type User \
  --role "Azure AI Project Manager" \
  --scope "$PROJECT_ID"
```

> The assignment may take several minutes to propagate. If `azd deploy` reports an `AuthorizationFailed` or missing `roleAssignments/write` permission error, this role assignment may not have propagated yet.

---

## Step 1. Open the Repository

Open VS Code, then open this lab (the commands are the same on Windows, Linux, and macOS).

```bash
cd labs/lab2-hosted-agent-deploy
code .
```

---

## Step 2. Configure Environment Variables

Open the target project in the Foundry portal and note the following values:

1. **Project endpoint** — Available on the project's Overview page  
   Format: `https://<account>.services.ai.azure.com/api/projects/<project>`
2. **Model deployment name** — Available under Models + endpoints (for example, `gpt-5.2`; use the exact name assigned during deployment)

Copy `.env.example` to create `.env`, then edit it.

#### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
notepad .env
```

#### Linux / macOS (bash)

```bash
cp .env.example .env
${EDITOR:-vi} .env
```

Example `.env` file (both values are required):

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://contoso.services.ai.azure.com/api/projects/contoso-proj
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5.2
```

---

## Step 3. Create the Subagents

Create the two subagents that the orchestrator will invoke: a Microsoft technology expert and a Web search agent.

| Agent Name (Fixed) | Tool | Purpose |
| --- | --- | --- |
| `ms-learn` | [Microsoft Learn MCP Server](https://learn.microsoft.com/api/mcp) (`MCPTool`) | Answer Microsoft technology questions based on Microsoft Learn documentation |
| `web-search` | Foundry `WebSearchTool` (Bing Search grounding) | Answer general questions using current information from the Web |

[`scripts/provision_agents/provision_agents.py`](scripts/provision_agents/provision_agents.py) uses the Foundry SDK (`azure-ai-projects`) to create these as Prompt Agents. The script uses the `.env` file created in Step 2 (`FOUNDRY_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME`) without modification.

> **Note** — If agents with the same names already exist, the script only **adds new versions** and does not overwrite existing data. The orchestrator is configured to always use the latest version, so running the script multiple times does not affect its behavior.

Create and use a virtual environment dedicated to the script because its dependencies differ from those of the orchestrator itself.

#### Windows (PowerShell)

```powershell
cd scripts\provision_agents
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
az login
python provision_agents.py
cd ..\..
```

#### Linux / macOS (bash)

```bash
cd scripts/provision_agents
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
az login
python provision_agents.py
cd ../..
```

After the script finishes, confirm that `ms-learn` and `web-search` appear in the **Agents** list in the Foundry portal. You can also test each agent in the playground (for example, ask `ms-learn`, "What is Azure Foundry?" and ask `web-search`, "What is today's weather in Tokyo?").

---

## Step 4. Review Agent Skills and Customize the Output Format

Open the canonical runtime file `agent-src/skills/orchestrator-routing/SKILL.md`.  
This file defines the **multi-agent routing logic that determines when to invoke each subagent**. The orchestrator's own `instructions` in `agent-src/orchestrator.py` contain no routing logic; all routing control is provided through the skill.

An [English reference translation](agent-src/skills/orchestrator-routing/SKILL_EN.md) is available for reading, but the deployed agent loads the canonical `SKILL.md`.

Add an output-format section that **standardizes answers as reports**. Append the following section to the end of `SKILL.md`, then save the file:

```markdown
## Output Format

Always present the final answer in the following report format (Markdown).

### Summary
(Summarize the answer to the question in 2–3 sentences.)

### Details
(Organize and present the information obtained from the subagents.)

### References
(List referenced URLs and sources as bullet points. Write "None" if there are none.)
```

> Saving the file applies the change; no rebuild or other action is required.

---

## Step 5. Verify the Behavior Locally

Run the application locally from the `agent-src/` directory. `load_dotenv()` searches parent directories to find `.env` at the lab root, so you can leave `.env` there.

#### Windows (PowerShell)

```powershell
cd agent-src
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
az login
python local.py
```

#### Linux / macOS (bash)

```bash
cd agent-src
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
az login
python local.py
```

At the interactive prompt, try questions like the following to verify the routing and output format.

| Example Input | Expected Behavior |
| --- | --- |
| `What is a Hosted Agent in Microsoft Foundry?` | Invoke only `ms_learn_agent` |
| `What is today's weather in Tokyo?` | Invoke only `web_search_agent` |
| `Compare Microsoft Agent Framework with other frameworks.` | Invoke both agents and combine their results |

The test succeeds if every answer uses the **Summary / Details / References** report format.

---

## Step 6. Deploy as a Foundry Hosted Agent

Use **Azure Developer CLI (`azd`)** for the simplest deployment process. The container image is **built remotely in ACR**, so you do not need to install Docker locally. `azd` uses the `Dockerfile` and `agent.manifest.yaml` included in `agent-src/` without modification.

> **Important** — Run the following commands from the **lab root** (the parent directory of `agent-src/`). If you ran `cd agent-src` in Step 5, return to the root with `cd ..`. `azd ai agent init` copies the manifest directory (`agent-src/`) to `./src/maf-skills-orchestrator/` and uses it as the deployment source.

> **First and subsequent deployments** — For the first deployment, when infrastructure such as ACR must be created, use **`azd up`** to provision and deploy with one command. When only the code has changed, use **`azd deploy`**.

> **If `azd ai agent init` hangs after `Manifest validated successfully`** — If the `.venv` directories created in Steps 3 and 5 (`agent-src/.venv` and `scripts/provision_agents/.venv`) remain in the repository, the file scan performed by `azd ai agent init` may not finish. Stop the command, remove the `.venv` directories as shown below, and run it again.
>
> #### Windows (PowerShell)
>
> ```powershell
> Remove-Item -Recurse -Force .\agent-src\.venv -ErrorAction SilentlyContinue
> Remove-Item -Recurse -Force .\scripts\provision_agents\.venv -ErrorAction SilentlyContinue
> ```
>
> #### Linux / macOS (bash)
>
> ```bash
> rm -rf ./agent-src/.venv ./scripts/provision_agents/.venv
> ```

### Commands

#### Windows (PowerShell)

```powershell
# 0. Move to the Lab 2 root directory
cd ..

# 1. Sign in to azd (first use or after the session expires)
azd auth login

# 2. Initialize the azd project and associate it with the Foundry project (see the table below for interactive prompts)
azd ai agent init -m .\agent-src\agent.manifest.yaml

# 3. Provision infrastructure (including ACR), build, push to ACR, and create the Hosted Agent version
azd up
```

#### Linux / macOS (bash)

```bash
# 0. Move to the Lab 2 root directory
cd ..

# 1. Sign in to azd (first use or after the session expires)
azd auth login

# 2. Initialize the azd project (see the table below for interactive prompts)
azd ai agent init -m ./agent-src/agent.manifest.yaml

# 3. Provision infrastructure (including ACR), build, push to ACR, and create the Hosted Agent version
azd up
```

### `azd ai agent init` Interactive Prompts

The following prompts appear in order. For items where the default is acceptable, simply press Enter.

| Prompt | Input Guidance |
| --- | --- |
| `Continue initializing an app in '...'?` | Enter **y** to initialize at the repository root |
| `How would you like to configure model(s)?` | Select **Use existing model deployment(s) from a Foundry project** |
| `Select a tenant` | Select the Azure **tenant** with the arrow keys |
| `Select subscription` | Select the **Azure subscription** containing the Foundry project with the arrow keys |
| `Select a Foundry project` | Select the project whose endpoint you identified in Step 2 |
| `Select deployment` (for gpt-5.2) | Select the existing model deployment identified in Step 2 |
| `Select container resource allocation` | The default **`0.25 cores, 0.5Gi memory`** is sufficient |

> **Note** — After you answer all prompts, `azd ai agent init` performs the following tasks:
> - Copies the contents of `agent-src/` to `src/maf-skills-orchestrator/`
> - Resolves the `{{AZURE_AI_MODEL_DEPLOYMENT_NAME}}` placeholder in `agent.manifest.yaml` with the selected model name and generates `src/maf-skills-orchestrator/agent.yaml`
> - Adds a `services: maf-skills-orchestrator` section to `azure.yaml`
> - Adds Bicep templates for ACR, Application Insights, and other infrastructure under `infra/`

### Verify the Completed `azd up`

Confirm that `maf-skills-orchestrator` appears in the **Agents** list in the Foundry portal.

### Verify Responses in the Foundry Portal

1. Open the project in the Foundry portal at [https://ai.azure.com](https://ai.azure.com).
2. In the left menu, select **Agents → `maf-skills-orchestrator`**.
3. Enter the same questions from Step 5 in the **Playground** on the right.
4. Verify the routing behavior and the **Summary / Details / References** response format.

> **If the Playground displays `Network error`**  
> When the subagents (Microsoft Learn and Web search) take a long time to respond, the Foundry Playground frontend may time out first and display `Network error`. The Hosted Agent container continues processing normally. In that case, use the following `azd` command to verify the behavior through the CLI:
>
> ```bash
> azd ai agent invoke maf-skills-orchestrator "What is a Hosted Agent in Microsoft Foundry?"
> ```

---

## Step 7. Review Trace Logs by Enabling the Agent Framework OTel Extension

Foundry Hosted Agents **automatically configure the OpenTelemetry pipeline to Application Insights at the container host level**. However, the GenAI spans emitted by **Agent Framework** (`load_skill`, calls to tools such as `ms_learn_agent` and `web_search_agent`, and prompt and response bodies) are not sent unless the framework calls **`enable_instrumentation()`**. Without this call, the trace UI in the Foundry portal shows only the agent invocation and final response, without a breakdown of subagent calls.

In this step, you will **add one line to both the entry point and manifest** and redeploy the agent, then verify that more detailed traces are available.

> **Files to edit** — When you ran `azd ai agent init` in Step 6, it copied files from `agent-src/` to **`src/maf-skills-orchestrator/`**. This copied directory is the deployment source that `azd deploy` actually uses. In this step, edit files directly under **`src/maf-skills-orchestrator/`**, not `agent-src/`.

### 7-1. Add `enable_instrumentation()` to `src/maf-skills-orchestrator/main.py`

Open `src/maf-skills-orchestrator/main.py`, make the following **two changes**, and save the file.

1. Add the import:

   ```python
   from agent_framework.observability import enable_instrumentation
   ```

2. Add one line inside `main()`, **before** the call to `build_orchestrator()`:

   ```python
   def main() -> None:
       load_dotenv()
       enable_instrumentation()        # Add this line
       agent = build_orchestrator()
       server = ResponsesHostServer(agent)
       server.run()
   ```

### 7-2. Add Environment Variables to `src/maf-skills-orchestrator/agent.yaml`

Open `src/maf-skills-orchestrator/agent.yaml`. This file was generated from `agent.manifest.yaml` when you ran `azd ai agent init` in Step 6, and it already contains environment variables such as `AZURE_AI_MODEL_DEPLOYMENT_NAME`. Append the following two entries using the same indentation and list marker (`-`) as the existing entries:

```yaml
    # Send Agent Framework GenAI spans to Application Insights
    - name: ENABLE_INSTRUMENTATION
      value: "true"
    # Include prompt and response bodies in span attributes so they are visible in the Foundry trace UI
    # (Use with caution in production because these values may contain sensitive data)
    - name: ENABLE_SENSITIVE_DATA
      value: "true"
```

> ⚠️ `ENABLE_SENSITIVE_DATA=true` includes subagent inputs and return values in traces. **Set it to `false` or remove this entry in production.**

### 7-3. Redeploy

```bash
azd deploy
```

You do not need to edit `agent-src/`; `azd` builds directly from `src/maf-skills-orchestrator/`.

### 7-4. Review Traces in the Foundry Portal

1. Open the [Foundry portal](https://ai.azure.com).
2. In the project, select **Agents → `maf-skills-orchestrator`** from the left menu.
3. Run a question in the **Playground**, then select the **trace ID** displayed in the response (or open the **Tracing** or **Monitoring** tab).
4. The test succeeds if the expanded span hierarchy includes:
   - The root `invoke_agent ...` span for the entire orchestrator
   - A `chat <model>` span for the Foundry LLM call
   - `execute_tool load_skill` for loading the Agent Skill
   - `execute_tool ms_learn_agent` and/or `execute_tool web_search_agent` for subagent calls
   - Input and output message bodies in each span's attributes (`gen_ai.input.messages`, `gen_ai.output.messages`, and so on)

> **Note** — Traces can take **30–60 seconds** to appear in the trace UI. Wait briefly after redeploying before checking.

> **More detailed analysis** — Open the Application Insights resource associated with the Foundry project directly in the Azure portal to analyze execution time, failure rate, and token usage with custom Kusto queries.

---

## Clean Up

The command is the same on Windows, Linux, and macOS:

```bash
azd down
```

---

## File Structure

```
.
├── README_EN.md                      # This file
├── README.md                         # Japanese guide
├── .env.example                      # Environment variable template (create `.env` in the lab root)
├── .gitignore
├── scripts/                          # Workshop scripts
│   └── provision_agents/             # Step 3: Create subagents (Microsoft Learn MCP / Web search)
│       ├── provision_agents.py
│       └── requirements.txt
└── agent-src/                        # Everything below this directory is deployed to the Hosted Agent container
    ├── .dockerignore
    ├── Dockerfile                    # For the Hosted Agent (linux/amd64, port 8088)
    ├── agent.manifest.yaml           # Manifest for azd ai agent init
    ├── requirements.txt              # Python dependencies
    ├── orchestrator.py               # Builds the orchestrator (Agent + Skills + as_tool)
    ├── main.py                       # Hosted entry point (ResponsesHostServer)
    ├── local.py                      # Local CLI entry point (not used in the container)
    └── skills/
        └── orchestrator-routing/
            ├── SKILL.md              # Deployed multi-agent routing skill (Agent Skills)
            └── SKILL_EN.md           # English reference translation
```

## Reference Documentation

- [Agent Skills (Python)](https://learn.microsoft.com/en-us/agent-framework/agents/skills?pivots=programming-language-python)
- [Foundry Hosted Agents (Python)](https://learn.microsoft.com/en-us/agent-framework/hosting/foundry-hosted-agent)
- [Deploy a hosted agent](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/deploy-hosted-agent)
- [`FoundryAgent` / `FoundryChatClient`](https://learn.microsoft.com/agent-framework/agents/providers/microsoft-foundry?pivots=programming-language-python)
- [Official sample: `agent-framework/python/samples/04-hosting/foundry-hosted-agents`](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting/foundry-hosted-agents)
