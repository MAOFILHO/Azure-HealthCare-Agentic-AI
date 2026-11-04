# CareCompanion

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![azure-ai-projects](https://img.shields.io/badge/azure--ai--projects-2.7.0-0078D4?logo=microsoftazure&logoColor=white)
![openai](https://img.shields.io/badge/openai-3.42.0-412991?logo=openai&logoColor=white)
![Agent Framework](https://img.shields.io/badge/Agent%20Framework-1.x-5E5E5E?logo=microsoft&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-2.x-000000?logo=modelcontextprotocol&logoColor=white)
![Microsoft Foundry](https://img.shields.io/badge/Microsoft-Foundry-0078D4?logo=microsoft&logoColor=white)
![Bicep](https://img.shields.io/badge/IaC-Bicep-0078D4?logo=microsoftazure&logoColor=white)
![pytest](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

[![CI](https://github.com/MAOFILHO/Azure-HealthCare-Agentic-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/MAOFILHO/Azure-HealthCare-Agentic-AI/actions/workflows/ci.yml)

CareCompanion is a patient-services assistant for Northfield General, a fictional hospital. It answers visiting-hours and billing questions from policy documents, looks up demo patients and appointments, reads a discharge note, and runs small multi-agent workflows. It is built in seven labs that follow the AI-103 healthcare lab guide (`docs/User_Guide.pdf`). All infrastructure is Bicep, deployed and destroyed by two scripts: zero Azure portal clicks. All data is synthetic.

## Why this is production-grade

- Infrastructure as code: one `az deployment sub create` builds the resource group, Foundry resource, project, model deployments and role assignments.
- Least privilege: two roles, scoped to the Foundry resource only (`infra/roles.bicep`).
- No secrets in the repo: sign-in is `az login`, read by `azure-identity` credentials. The deploy script writes endpoints to a git-ignored file with mode 600 and never prints them.
- Safe teardown: `infra/destroy.sh` deletes nothing unless you type the resource group name. `src/lab07_cleanup.py` deletes only the agents and vector stores the labs created.
- Offline tests: every lab and script has tests that run without Azure access.
- CI on every pull request to `staging`: `pytest`, then `az bicep build` on each template.

## Architecture

![CareCompanion architecture on Microsoft Foundry](docs/images/architecture.png)

Source: [docs/Architecture_Overview.pdf](docs/Architecture_Overview.pdf).

### Agent structure

Lab 6 runs two multi-agent patterns. In the care team (`src/lab06_care_team.py`), the coordinator calls each specialist as a tool, and only the specialists touch the hospital data. In the pipeline (`src/lab06_pipeline.py`), two agents run in a fixed order and each one passes its output to the next.

```mermaid
flowchart LR
    caller([Caller]) <--> coord

    subgraph care["Care team (lab06_care_team.py)"]
        coord["CareCoordinator<br/>orchestrator"]
        records["RecordsSpecialist<br/>sub-agent"]
        sched["SchedulingSpecialist<br/>sub-agent"]
        coord <-- "records_specialist tool" --> records
        coord <-- "scheduling_specialist tool" --> sched
    end

    records --> find["find_patient"]
    sched --> getappt["get_appointments"]
    sched --> book["book_appointment"]
    find --> patients[("patients.json")]
    getappt --> appts[("appointments.json")]
    book --> appts
```

How the agents talk, for the Lab 6 demo request:

```mermaid
sequenceDiagram
    actor Caller
    participant C as CareCoordinator
    participant R as RecordsSpecialist
    participant S as SchedulingSpecialist
    Caller->>C: Book Maria Rivera's cardiology follow-up if missing
    C->>R: records_specialist("Maria Rivera")
    R->>R: find_patient tool
    R-->>C: patient record and ID
    C->>S: scheduling_specialist(patient ID)
    S->>S: get_appointments tool
    alt no cardiology follow-up
        S->>S: book_appointment tool
    end
    S-->>C: appointments or new booking
    C-->>Caller: one complete answer
```

The pipeline needs no orchestrator. Each agent hands its output to the next:

```mermaid
flowchart LR
    note[("discharge_note.md")] --> extractor["NoteExtractor<br/>facts as bullets"]
    extractor -- "extracted facts" --> writer["PatientWriter<br/>plain-language rewrite"]
    writer --> summary(["After-visit summary"])
```

Every agent calls the same Foundry chat deployment through `FoundryChatClient`. Specialists answer only through the coordinator. They never reply to the caller directly.

### Resources

```
            az login (azure-identity credentials)
                          |
  infra/deploy.sh --> infra/main.bicep (subscription scope)
                          |
              Resource group (eastus2)
                          |
          Foundry resource (AIServices, S0)
           |-- Foundry project
           |     |-- agent carecompanion-agent    (lab02, lab04)
           |     |-- vector store northfield-policies (lab04)
           |-- deployment gpt-5-mini              (chat)
           |-- deployment text-embedding-3-large  (file search)
           |-- Content Understanding              (lab05)
           |-- roles: Azure AI User, Cognitive Services User

  src/lab0*.py ---- reads ----> data/
                                 |-- patients.json, appointments.json  (lab03, lab06 tools)
                                 |-- policies/*.md                     (lab04 vector store)
                                 |-- discharge_note.pdf                (lab05 input)
                                 |-- discharge_note.md                 (lab05 output, lab06 input)

  src/lab07_mcp.py ----> Microsoft Learn MCP server (public docs)
```

How the agent stays grounded in `data/`:

- Facts about patients and appointments come only from tool calls. `src/hospital_tools.py` exposes `find_patient`, `get_appointments` and `book_appointment` over the JSON files. Booking is a mock and saves nothing.
- Policy answers come only from documents. Lab 4 indexes `data/policies/*.md` into a vector store and attaches file search. The instructions tell the agent to answer only from what it finds and to say so when the documents do not cover a question.
- The instructions also set hard rules: emergencies go to 911 first, and clinical questions go to the nurse line, never to the model.

## The problem and the solution

**Problem.** Northfield General's front desk answers the same questions all day: visiting hours, upcoming appointments, billing, discharge paperwork. Staff time goes to lookups, and answers drift from written policy.

**Solution.** A Foundry agent that handles routine logistics only. It quotes hospital policy from the source documents, checks records through tools, turns a discharge note into structured data and a plain-language summary, and refuses to give medical advice.

## Results and impact

Measured in this repo:

- Offline tests pass with `python -m pytest`.
- `az bicep build` succeeds on all 5 templates in `infra/`.

## Lab pipeline

| Lab | Script | What you build | Key service |
|---|---|---|---|
| 1 | `src/lab01_chat.py` | First model call | Foundry model deployment |
| 2 | `src/lab02_create_agent.py`, `src/lab02_chat.py` | Agent with instructions, multi-turn chat | Foundry Agent Service |
| 3 | `src/lab03_tools.py` | Function calling over demo records | Microsoft Agent Framework |
| 4 | `src/lab04_knowledge.py` | Answers grounded in policy files | File search, vector store |
| 5 | `src/lab05_extract.py`, `src/lab05_structured.py` | Discharge note to Markdown, then JSON | Azure Content Understanding |
| 6 | `src/lab06_care_team.py`, `src/lab06_pipeline.py` | Coordinator with specialists, sequential workflow | Agent Framework orchestrations |
| 7 | `src/lab07_mcp.py`, `src/lab07_cleanup.py` | Agent with an MCP tool, then cleanup | Microsoft Learn MCP server |

### Lab 1: first model call
Sends one prompt to the chat deployment. Proves sign-in, endpoint and model work.

### Lab 2: the agent
Creates `carecompanion-agent` with its safety instructions, then chats with it over a server-side conversation.

### Lab 3: function calling
Gives the agent the three tools in `src/hospital_tools.py` so it can find a patient, list appointments and book a mock lab draw.

### Lab 4: grounded answers
Indexes the three policy files and attaches file search. The agent answers an ICU visiting question from the documents.

### Lab 5: discharge note
Extracts `data/discharge_note.pdf` to Markdown, then asks the model for a JSON record of diagnosis, medications, follow-up and warning signs.

### Lab 6: multi-agent workflows
A coordinator consults records and scheduling specialists. A second workflow turns the discharge note into an after-visit summary.

### Lab 7: MCP and cleanup
Connects an agent to the Microsoft Learn MCP server, then removes the agents and vector stores the labs created.

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.12 |
| Infrastructure | Bicep, Azure CLI |
| Foundry SDK | `azure-ai-projects` |
| Agent framework | `agent-framework-core`, `agent-framework-foundry`, `agent-framework-orchestrations` |
| Model client | `openai` |
| Document extraction | `azure-ai-contentunderstanding` |
| MCP | `mcp` |
| Auth | `azure-identity` |
| Tests | `pytest` |
| CI | GitHub Actions |

### Azure services

| Service | Use |
|---|---|
| Resource group | Holds everything; deleted by `infra/destroy.sh` |
| Foundry resource (AIServices, S0) | Hosts models, Content Understanding and the project |
| Foundry project | Agents, conversations, vector stores |
| `gpt-5-mini` (GlobalStandard, 50K TPM) | Chat and agents |
| `text-embedding-3-large` (GlobalStandard, 50K TPM) | Embeddings for file search |
| Role assignments | Azure AI User, Cognitive Services User for the signed-in principal |

## Prerequisites and setup

- An Azure subscription where you can create resource groups.
- Azure CLI with Bicep.
- Python 3.12.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
az login
```

## Running the project

This is the full dry-run: deploy, all 7 labs in order, cleanup, teardown. Run every command from the repo root with the virtual environment active (see Prerequisites and setup). [docs/RUNBOOK.md](docs/RUNBOOK.md) has the same steps with more detail.

Never print or commit `.env` or `.env.foundry`. Use demo data only.

### Step 1: Deploy

```bash
az login
infra/deploy.sh --what-if   # preview, changes nothing
infra/deploy.sh             # deploy, writes .env.foundry
cp .env.foundry .env        # the labs read .env
```

Expected from the deploy: `Deployed. Wrote 3 variables to the env file (values not shown).`

### Step 2: Run the labs, in order

Each lab calls the live Foundry project. The Foundry service sometimes answers `404 Subdomain does not map to a resource` for a few seconds. Lab 4 and the cleanup script retry on their own. For any other lab, wait a minute and run it again.

Lab 2b needs Lab 2a first, because it chats with the agent that 2a creates. Run the labs in the order below. Your wording will differ from the screenshots, because the model writes the text.

#### Lab 1: first model call

```bash
python src/lab01_chat.py
```

You should see a two-sentence description of a hospital care coordinator.

![Lab 1 output](docs/screenshots/Lab1.png)

#### Lab 2: create the agent, then chat

```bash
python src/lab02_create_agent.py
python src/lab02_chat.py
```

The first command prints `Agent 'carecompanion-agent' is now at version 1`. The number rises on a re-run. The second opens a `You:` prompt. Ask "What are the visiting hours?", then "My mother is in the hospital and I want to see her tomorrow.", then type `quit`.

![Lab 2 output](docs/screenshots/Lab2.png)

#### Lab 3: function calling

```bash
python src/lab03_tools.py
```

At the `You:` prompt, ask "Find Maria Rivera's upcoming appointments", then "Book a lab draw for July 24", then type `quit`. Booking is a mock and saves nothing.

Optional tracing: set `ENABLE_CONSOLE_EXPORTERS=true` before the command. Spans print to the terminal. Nothing goes to Azure.

![Lab 3 output](docs/screenshots/Lab3.png)

#### Lab 4: grounded answers from hospital policy

```bash
python src/lab04_knowledge.py
```

You should see one `Indexed <file>` line per policy file, the agent at a new version with file search attached, then an ICU visiting-hours answer drawn from the policy files. Your version number will differ.

![Lab 4 output](docs/screenshots/Lab4.png)

#### Lab 5: discharge note

```bash
python src/lab05_extract.py
python src/lab05_structured.py
```

The first command saves the extracted Markdown to `data/discharge_note.md` and prints the first lines. The second prints a JSON record with diagnosis, medications, follow-up plan and warning signs. `lab05_extract.py` rewrites `data/discharge_note.md`. Run `git restore data/discharge_note.md` if you do not want that change in your working tree.

![Lab 5 output](docs/screenshots/Lab5.png)

#### Lab 6: multi-agent workflows

```bash
python src/lab06_care_team.py
python src/lab06_pipeline.py
```

The first shows the coordinator checking the records and scheduling agents. It finds the existing cardiology follow-up for Maria Rivera. The second prints a plain-language after-visit summary that ends with the hospital contact number.

![Lab 6 output](docs/screenshots/Lab6.png)

#### Lab 7: MCP

```bash
python src/lab07_mcp.py
```

You should see an answer about the Foundry project endpoint, with a Microsoft Learn source. The lower half of the screenshot is Step 3 below.

![Lab 7 output](docs/screenshots/Lab7.png)

### Step 3: Clean up the lab objects

```bash
python src/lab07_cleanup.py
```

Expected: one `Deleting vector store` or `Deleting agent` line per object, then `Lab agents and vector stores cleared.` It deletes only `carecompanion-agent` and `northfield-policies`.

### Step 4: Tear down Azure

```bash
infra/destroy.sh            # asks you to type the group name: K21-project-rg
az cognitiveservices account purge --name k21-carecompanion --resource-group K21-project-rg --location eastus2
rm -f .env .env.foundry
```

Expected: `Deleted K21-project-rg.` A wrong name deletes nothing. Billing stops once the group is deleted.

Deploying again after `infra/destroy.sh`: the script deletes the resource group only, so the Foundry account stays soft-deleted. A new deploy with the same `foundryName` (default `k21-carecompanion` in `infra/main.bicep`) fails with `FlagMustBeSetForRestore`. Run the `purge` command above first, or set a new `foundryName`.

## Project structure

```
.
|-- .github/workflows/ci.yml   pytest + az bicep build on PRs to staging
|-- data/
|   |-- patients.json, appointments.json   demo records
|   |-- policies/                          billing, discharge, visiting hours
|   |-- discharge_note.pdf                 synthetic discharge note
|-- docs/
|   |-- RUNBOOK.md                         deploy, run, clean up, destroy
|   |-- User_Guide.pdf, Architecture_Overview.pdf, Project_Overview.pdf
|-- infra/
|   |-- main.bicep, foundry.bicep, models.bicep, roles.bicep, budget.bicep
|   |-- deploy.sh, destroy.sh
|-- src/
|   |-- hospital_tools.py                  agent tools over data/
|   |-- lab01_chat.py ... lab07_cleanup.py
|-- tests/                                 offline tests, one file per area
|-- requirements.txt
```

## Running tests

```bash
python -m pytest
```

The tests need no Azure access. CI also runs `az bicep build --file <template> --stdout` on each file in `infra/`.

## Azure region and cost

- Region: `eastus2` (East US 2), the default in `infra/main.bicep` and `infra/deploy.sh`. The User Guide uses the same region.
- Cost: the User Guide estimates $1 to $2 for the 3 to 4 hours the labs take. That figure includes a lab VM, which this repo does not deploy. Run `infra/destroy.sh` when you finish so nothing keeps billing.
- Budget (optional): `infra/deploy.sh --budget-email ADDRESS` also deploys `infra/budget.bicep`, a 20 USD monthly budget that emails alerts at 75% and 100% of actual cost. Pass the address on the command line; never commit it. See [docs/RUNBOOK.md](docs/RUNBOOK.md).

## Key engineering decisions

| Decision | Why |
|---|---|
| Bicep for all infra, no portal clicks | Repeatable deploys and a clean teardown |
| Roles scoped to the Foundry resource | Nothing wider than the labs need |
| Endpoints written to a git-ignored file, never printed | Public repo; no values in logs or commits |
| `az login` and `azure-identity` credentials, no keys | No secrets to store or rotate |
| Model deployments created one at a time | Parallel deployments on one account can fail with `RequestConflict` |
| Destroy asks for the resource group name | One typo cannot delete the wrong group |
| Cleanup deletes only lab-named objects | Other agents in the project are left alone |
| Offline tests with fakes | CI runs without an Azure subscription |

## Author

Marcos Oliveira ([@MAOFILHO](https://github.com/MAOFILHO))

License: MIT
