# Prerequisites (Setup)

**English** | [日本語](setup.md)

Before starting this workshop, prepare your environment by following the steps below.
**Estimated time: Approximately 30 minutes**

> ⚠️ Large downloads may take a long time over the venue Wi-Fi on the day of the workshop.
> Be sure to complete these steps **in advance**.

---

## ✅ Prerequisites Checklist

- [ ] [1. Check Accounts and Permissions](#1-check-accounts-and-permissions)
- [ ] [2. Install Tools](#2-install-tools)
- [ ] [3. Set Up VS Code](#3-set-up-vs-code)
- [ ] [4. Clone the Repository and Configure Environment Variables](#4-clone-the-repository-and-configure-environment-variables)
- [ ] [5. Verify Your Setup](#5-verify-your-setup)

---

## 1. Check Accounts and Permissions

### 1.1 Azure Subscription

- Have an active Azure subscription
- Role: **Contributor** or higher (**Owner** or **User Access Administrator** is recommended for Hosted Agent deployment)
- Region: **North Central US** (a current Hosted Agent limitation)

- For the May 18 workshop, you may also use an environment provided by Microsoft. See the separate PowerPoint presentation shared in the room for sign-in information and instructions for this environment.

### 1.2 GitHub Account (Optional)

- Used to fork or clone this repository

---

## 2. Install Tools

### 2.1 Python 3.11+

- Official site: https://www.python.org/downloads/

```powershell
# PowerShell (Windows)
python --version    # Verify that version 3.11 or later is displayed
# If it is not displayed, try the py command
py --version
```

```bash
# Bash (macOS / Linux)
python3 --version
```

### 2.2 uv (Python Package Manager)

```powershell
# PowerShell
pip install uv
```

```bash
# Bash
pip install uv
# Or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.3 Azure CLI (`az`)

- Official site: https://learn.microsoft.com/cli/azure/install-azure-cli

```powershell
# PowerShell (Windows) — winget is available
winget install -e --id Microsoft.AzureCLI
```

```bash
# Bash (macOS)
brew install azure-cli
```

### 2.4 Azure Developer CLI (`azd`)

- Official site: https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd

```powershell
# PowerShell (Windows)
winget install Microsoft.Azd
```

```bash
# Bash (macOS)
brew tap azure/azd && brew install azd
```

The AI Agent extension for `azd` is also required:

```bash
azd ext install azure.ai.agents
```

---

## 3. Set Up VS Code

### 3.1 Visual Studio Code

- Official site: https://code.visualstudio.com/download

### 3.2 Recommended Extensions

| Extension | Purpose |
|---|---|
| Python (`ms-python.python`) | Python development |
| Azure Tools (`ms-vscode.vscode-node-azure-pack`) | Manage Azure resources |
| Microsoft 365 Agents Toolkit | Scaffold agent samples |

In VS Code, press `Ctrl + Shift + X` (macOS: `Cmd + Shift + X`), search for each extension by name, and install it.

---

## 4. Clone the Repository and Configure Environment Variables

### 4.1 Clone the Repository

```bash
git clone https://github.com/<your-org>/Foundry-in-a-Day-Developer-Edition.git
cd Foundry-in-a-Day-Developer-Edition
```

### 4.2 Create the Environment Variable File

```powershell
# PowerShell
Copy-Item .env.example .env
```

```bash
# Bash
cp .env.example .env
```

Open `.env` and replace the values with those from your Foundry project.

> 🔒 `.env` is already included in `.gitignore`. **Never commit secrets.**

### 4.3 Set Up the Virtual Environment

```bash
uv venv
# PowerShell
.venv\Scripts\Activate.ps1
# Bash
source .venv/bin/activate

uv pip install -e .
```

---

## 5. Verify Your Setup

Your setup is complete if all of the following commands succeed:

```bash
python --version            # 3.11 or later
uv --version                # Any version
az --version                # 2.80 or later recommended
azd version                 # 1.24.0 or later recommended
azd ext list                # Verify that ai.agents is included
```

Sign in to Azure:

```bash
az login
azd auth login
```

---

## 🆘 If You Encounter a Problem

- Environment setup issues: See [troubleshooting_EN.md](troubleshooting_EN.md)
- On the day of the workshop: Ask a staff member or teaching assistant at the venue

---

## 💡 Operating System Notes

- **Windows**: If `python` is not on your `PATH`, use `py -3.11`
- **Windows**: Recommended line-ending configuration — `git config --global core.autocrlf input`
- **macOS**: Use Python installed through Homebrew or pyenv instead of the system Python
- **Corporate proxy environments**: Configure the proxy separately for `pip`, `uv`, and `az` (see [troubleshooting_EN.md](troubleshooting_EN.md))
