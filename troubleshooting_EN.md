# Troubleshooting

**English** | [日本語](troubleshooting.md)

This document summarizes common workshop issues and how to resolve them.
If you encounter a new issue, share it with a teaching assistant or instructor and add it to this file.

> 💡 First, check the lab's **"Common Errors"** section. If the issue remains unresolved, refer to this document.

---

## Table of Contents

- [Azure Authentication](#azure-authentication)
- [Region and Quota Constraints](#region-and-quota-constraints)
- [Network and Proxy](#network-and-proxy)
- [Python and uv Installation](#python-and-uv-installation)
- [VS Code Extensions](#vs-code-extensions)
- [Character Encoding and Line Endings](#character-encoding-and-line-endings)

---

## Azure Authentication

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| `DefaultAzureCredential` fails | The `az` or `azd` authentication session has expired | Run `az login` or `azd auth login` again | Labs 1–3 |
| `AuthenticationError` | Tenant or subscription mismatch | Switch subscriptions with `az account set --subscription <id>` | Labs 1–3 |
| | | | |

---

## Region and Quota Constraints

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| Region error during Hosted Agent deployment | Hosted Agents support only **North Central US** at the time of writing | Specify `--location northcentralus` when running `azd init` | Lab 2 |
| `429 Too Many Requests` | Model rate limit | Wait and try again, or check the model quota | Labs 1–3 |
| `DeploymentNotFound` | The model deployment name does not match | Check **Build → Deployments** in the Foundry portal and update `.env` | Labs 1–3 |
| | | | |

---

## Network and Proxy

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| `pip` or `uv` installation times out | Corporate proxy is not configured | Set the `HTTP_PROXY` and `HTTPS_PROXY` environment variables | Setup |
| `az login` does not open a browser | Corporate proxy or SSO restrictions | Try `az login --use-device-code` | Setup |
| | | | |

---

## Python and uv Installation

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| `python: command not found` (Windows) | `PATH` is not configured | Use `py -3.11` or add Python to `PATH` | Setup |
| `uv pip install` returns an SSL error | Corporate certificate requirements | Set `REQUESTS_CA_BUNDLE` to the corporate CA certificate | Setup |
| | | | |

---

## VS Code Extensions

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| Samples do not appear in Microsoft 365 Agents Toolkit | The extension is outdated | Update to the latest version and restart VS Code | Lab 1 |
| | | | |

---

## Character Encoding and Line Endings

| Symptom | Possible Cause | Solution | Commonly Affected Labs |
|---|---|---|---|
| Japanese text is garbled in the terminal (Windows) | Code page mismatch | Switch to UTF-8 with `chcp 65001` | General |
| `git diff` reports many line-ending changes | Mixed CRLF and LF line endings | Run `git config --global core.autocrlf input` | General |
| | | | |

---

## If the Issue Persists

- Ask a staff member or teaching assistant at the venue
- Open an issue in the repository and include a prefix such as `[lab1]` in the title
