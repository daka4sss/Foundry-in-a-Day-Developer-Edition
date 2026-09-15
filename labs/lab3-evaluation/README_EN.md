<!--
============================================================
This file was created by copying ../../lab-template.md.
Do not remove the section headings (## Goals through ## Next Lab).
Complete the placeholders with the lab content.
============================================================
-->

# Lab 3: Evaluate Your Agent

**English** | [日本語](README.md)

> **Owner**: TBD
> **Estimated duration**: Approximately 45 minutes

---

## Goals

After completing this lab, you will be able to:

- [ ] Systematically evaluate agent quality, safety, and agent performance with Microsoft Foundry **built-in evaluators**
- [ ] Create a **custom evaluator (Custom Grader)** to quantitatively assess agent-specific criteria, such as tool-selection accuracy
- [ ] Run **AI red teaming** in the cloud to identify agent vulnerabilities before production deployment

---

## What You Will Learn

- How to create and run evaluation jobs and retrieve results using the Foundry **Evals API** (`openai_client.evals`)
- Built-in evaluators: fluency, coherence, task adherence, safety (violence, hate, and self-harm), and agent performance (intent resolution, groundedness, and relevance)
- Custom evaluation using `python` graders and `score_model` graders (LLM-as-a-judge)
- Adversarial testing with the AI Red Teaming Agent, including attack strategies, evaluation taxonomies, and attack success rates
- How to review results on the **Evaluations** page in the Foundry portal

---

## Prerequisites

Complete the following before starting:

- [ ] Complete [Lab 2](../lab2-hosted-agent-deploy/README_EN.md) (optional because this lab can be completed independently)
- [ ] Create a Foundry project
- [ ] Install **VS Code** with the Python and Jupyter extensions
- [ ] Configure the required environment variables in `.env` as described below

---

## Instructions

> 💡 In this lab, you will run three evaluation-workshop notebooks from a separate repository.
> Exercises 1–3 each correspond to one notebook.

> ⚠️ **General note**: Work through each notebook while reviewing the output from every cell. Each notebook ends with a **cleanup cell**, but you do not need to run it.

### Preparation: Clone the Repository and Set Up the Environment

The evaluation notebooks are in the separate [foundry-observability-workshop](https://github.com/notanaha/foundry-observability-workshop.git) repository. Run the following commands in any working folder:

```powershell
# 1. Clone the repository
git clone https://github.com/notanaha/foundry-observability-workshop.git
cd foundry-observability-workshop

# 2. Create and activate a Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt
```

Next, authenticate with Azure and prepare the environment-variable file:

```powershell
# 4. Sign in to Azure (add --tenant <TENANT_ID> if you have multiple tenants)
az login --tenant <tenant-id>

# 5. Copy sample.env to .env
cd /labs/notebooks
copy sample.env .env
```

Open `.env` in an editor and populate the following values from the Foundry portal. See the comments in `sample.env` for details about where to find them.

| Variable | Where to Find It |
|--------|---------|
| `TENANT_ID` | Azure portal → Microsoft Entra ID |
| `AZURE_AI_PROJECT_ENDPOINT` | Foundry portal → Project → Overview → Project endpoint |
| `AZURE_AI_MODEL_DEPLOYMENT_NAME` | Foundry portal → Models + endpoints → Name column |
| `MODEL_ENDPOINT` | AI Services endpoint: remove `/api/projects/...` from `AZURE_AI_PROJECT_ENDPOINT` to produce `https://<account>.services.ai.azure.com` |

Finally, open the repository in VS Code. After opening a notebook, use **Select Kernel** in the upper-right corner to select the `.venv` environment you created (Python 3.1x).

### Exercise 1: Evaluate an Agent with Built-in Evaluators

Open [`labs/notebooks/prompt-agents/lab-05-evaluation.ipynb`](https://github.com/notanaha/foundry-observability-workshop/blob/main/labs/notebooks/prompt-agents/lab-05-evaluation.ipynb) and run its cells from top to bottom.

This notebook presents the "test data → agent → response → evaluator → score" evaluation pipeline in three parts:

- **Part A — Quality evaluation**: Score response quality using the fluency, coherence, and task-adherence evaluators
- **Part B — Safety evaluation**: Run the built-in content safety evaluators for violence, hate and unfairness, and self-harm
- **Part C — Agent performance evaluation**: Measure agent behavior using intent resolution, groundedness, and relevance

### Exercise 2: Create a Custom Evaluator (Custom Grader)

Open [`labs/notebooks/prompt-agents/lab-06-evaluation-custom.ipynb`](https://github.com/notanaha/foundry-observability-workshop/blob/main/labs/notebooks/prompt-agents/lab-06-evaluation-custom.ipynb) and run its cells from top to bottom.

This notebook has two phases:

- **Phase 1**: Run an agent with the `search_flights`, `search_hotels`, and `search_car_rentals` Function Tools; collect the actual `function_call` values (tool names and parameters); and upload them to Foundry as a JSONL dataset
- **Phase 2**: Score the collected data with three custom evaluators:
  - `correct_tool_called` (`python`) — Whether the expected tool was selected (0.0 / 1.0)
  - `required_params_present` (`python`) — Whether all required parameters are present (partial credit is available)
  - `routing_quality` (`score_model`) — Overall evaluation of the routing decision using an LLM-as-a-judge (1–5)

The `python` grader runs in the Foundry sandbox as a `grade(sample, item)` function. Confirm that it can evaluate business-specific correctness that built-in evaluators cannot measure.

### Exercise 3: Red-Team an Agent (OPTIONAL)

Open [`labs/notebooks/prompt-agents/lab-07-redteam.ipynb`](https://github.com/notanaha/foundry-observability-workshop/blob/main/labs/notebooks/prompt-agents/lab-07-redteam.ipynb) and run its cells from top to bottom.

This notebook uses the AI Red Teaming Agent to run automated adversarial testing **in the cloud**.

- Create a red-team evaluation using agent-specific safety evaluators (`builtin.prohibited_actions`, `builtin.task_adherence`, and `builtin.sensitive_data_leakage`)
- Configure the `Flip`, `Base64`, and `IndirectJailbreak` attack strategies and the evaluation taxonomy (risk categories)
- Create a multi-turn, five-turn red-team run and poll the server-side process every 15 seconds
- Review the result counts (attack success rate) and save output items to a JSON file

> ⏳ Depending on the number of attack strategies and turns, a red-team scan can take **several minutes**. A continuing `in_progress` status is normal.

After the run, read the "Interpreting Results" and "Mitigation Strategies" sections at the end of the notebook to understand common vulnerability patterns in travel agents.

---

## Verification

The lab is complete when all of the following conditions are met:

- [ ] The evaluation and red-team runs in all three notebooks reach the `completed` status
- [ ] Each notebook displays a score for every query or attack item
- [ ] The **Evaluations** page in the Foundry portal displays the quality, safety, agent, custom, and red-team runs and their scores

Example screenshot:

![Successful result](./assets/success.png)

---

## Common Errors

| Symptom | Possible Cause | Resolution |
|---|---|---|
| `KeyError: 'AZURE_AI_PROJECT_ENDPOINT'` | `.env` has not been created or is outside `labs/notebooks/` | Copy `sample.env` to `labs/notebooks/.env` and configure its values |
| `ModuleNotFoundError: azure.ai.projects` or similar | The virtual environment is inactive, or the VS Code kernel is not `.venv` | Run `pip install -r requirements.txt` and select `.venv` as the kernel |
| `CredentialUnavailableError` or another authentication error | `az login` has not been run, or the tenant does not match | Run `az login`, adding `--tenant <TENANT_ID>` if necessary, and set `TENANT_ID` in `.env` |
| An evaluation run reaches `failed` | The model deployment name does not match, or the TPM quota is insufficient | Match `AZURE_AI_MODEL_DEPLOYMENT_NAME` in `.env` to the deployment name in the portal and check the quota |
| A red-team run remains `in_progress` for a long time | Expected behavior while multi-turn attacks are generated and run in the cloud | Wait for completion; it may take several minutes |

> If these steps do not resolve the issue, see [troubleshooting_EN.md](../../troubleshooting_EN.md).

---

## Challenge (Optional)

If you have extra time, complete optional Exercise 3 and red-team the agent.

Open [`labs/notebooks/prompt-agents/lab-07-redteam.ipynb`](https://github.com/notanaha/foundry-observability-workshop/blob/main/labs/notebooks/prompt-agents/lab-07-redteam.ipynb).

---

## Next Lab

→ You have completed the workshop 🎉 Great work!

If you have time, use the checklist in the [root README](../../README_EN.md) to verify completion.
