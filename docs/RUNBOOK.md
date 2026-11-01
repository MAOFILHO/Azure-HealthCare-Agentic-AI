# CareCompanion runbook

Deploy, run the labs in order, clean up. No Azure portal clicks: all infrastructure is Bicep, driven by two scripts.
Demo data only. Never paste endpoints, keys or patient data into this file, an issue or a PR.

## Before you start

- Azure CLI with Bicep, Python 3.12, and an Azure subscription you can create resource groups in.
- From the repo root, create the environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Sign in

```bash
az login
```

Expected: a browser sign-in, then a list of your subscriptions. Pick the one to bill with `az account set --subscription <id>`.

## 2. Deploy

Preview first. This changes nothing.

```bash
infra/deploy.sh --what-if
```

Expected: a what-if summary of the resource group, the Foundry resource and project, the chat and embedding model deployments, and the role assignments.

Then deploy.

```bash
infra/deploy.sh
```

Expected: `Deployed. Wrote 3 variables to the env file (values not shown).`

The script writes a git-ignored dotenv file at the repo root, named `.env.foundry`, holding the three Foundry values. The labs read a file named `.env` from the same folder, so copy it once. Do not print or commit either file.

```bash
cp .env.foundry .env
```

## 3. Run the labs

Run each command from the repo root with the virtual environment active. The order follows the User Guide, sections 8 to 11.

### Lab 1: first model call

```bash
python src/lab01_chat.py
```

Expected: a two-sentence description of a hospital care coordinator. This confirms the model connection, sign-in and deployment.

### Lab 2: create the agent, then chat

```bash
python src/lab02_create_agent.py
```

Expected: `Agent 'carecompanion-agent' is now at version 1` (the version rises on a re-run).

```bash
python src/lab02_chat.py
```

Expected: a prompt for multi-turn chat. Ask "What are the visiting hours?", then "My mother is in the hospital and I want to see her tomorrow." The agent keeps context, follows its safety instructions and does not guess hospital policy.

### Lab 3: function calling

```bash
python src/lab03_tools.py
```

Expected: the agent looks up Maria Rivera, lists her upcoming appointments, and books a lab draw for the requested day. Booking is a mock and persists nothing. The tools live in `src/hospital_tools.py`.

### Lab 4: grounded answers from hospital policy

```bash
python src/lab04_knowledge.py
```

Expected: one `Indexed <file>` line per policy document, the agent at a new version with file search attached, then an ICU visiting-hours answer drawn from the policy files.

### Lab 5: discharge note

```bash
python src/lab05_extract.py
```

Expected: the extracted Markdown is saved to `data/discharge_note.md` and the first lines are printed, with headings and patient details preserved.

```bash
python src/lab05_structured.py
```

Expected: a JSON record with the patient name, diagnosis, medications, follow-up plan and warning signs.

### Lab 6: multi-agent workflows

```bash
python src/lab06_care_team.py
```

Expected: the coordinator consults the records and scheduling agents and reports that Maria Rivera already has a cardiology follow-up in the required window, so no new appointment is booked.

```bash
python src/lab06_pipeline.py
```

Expected: a plain-language after-visit summary that keeps the original medical facts, adds no new advice, and ends with the hospital contact number.

### Lab 7: MCP

```bash
python src/lab07_mcp.py
```

Expected: the agent discovers the Microsoft Learn documentation tools, then answers what the Foundry project endpoint is and where to find it in the portal, grounded in the docs.

## 4. Clean up

Remove the agents and vector stores the labs created.

```bash
python src/lab07_cleanup.py
```

Expected: one `Deleting vector store` or `Deleting agent` line per object, then `Lab agents and vector stores cleared.`

## 5. Destroy

Delete the whole resource group. The script asks you to type the group name first.

```bash
infra/destroy.sh
```

Expected: after the name matches, `Deleted K21-project-rg.` A wrong name deletes nothing and exits with an error.

Then remove the two local dotenv files.

```bash
rm -f .env .env.foundry
```

## Checks

Run the offline tests any time. They need no Azure access.

```bash
python -m pytest
```
