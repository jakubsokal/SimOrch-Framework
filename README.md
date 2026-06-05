# SimOrch Shared Memory Orchestration for Multi-Agent RE Simulation

> The only framework purpose-built for simulating and evaluating multi-agent Requirements Engineering processes.

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61dafb.svg)](https://react.dev/)

---

## What is SimOrch?

SimOrch is a research framework for simulating and evaluating multi-agent Requirements Engineering (RE) elicitation sessions. A Requirements Engineer agent conducts structured interviews with one or more stakeholder agents, extracts and validates requirements and issues in real time using a dedicated analyst agent, and produces detailed evaluation reports across seven research dimensions.

Unlike general-purpose agent frameworks such as AutoGen, CrewAI, or LangGraph which provide generic orchestration primitives SimOrch is domain-specific. Every concept in the system maps directly to established RE methodology: agent personas, revelation strategies, traceability, behavioural validity, and ground truth coverage. No competing tool exists for this use case.

**Key capabilities:**

- Configurable RE and stakeholder agent personas with precise behavioural controls (communication style, questioning strategy, domain knowledge, revelation rate, and more)
- Shared memory architecture all agents read from and write to a common message store across the full simulation
- Automatic requirement and issue extraction by a dedicated analyst agent, with a RE-agent validation loop that catches missed items and corrections.
- Seven-dimension evaluation engine using SBERT semantic embeddings and TF-IDF cosine similarity
- Multi-provider LLM support: OpenAI, Anthropic, Groq, Gemini, and Ollama (fully local)
- React UI for scenario management, simulation monitoring, artefact viewing, and evaluation results

---

## How It Works

A simulation proceeds as follows:

1. A scenario YAML file defines the RE agent, stakeholder agents, LLM providers, conversation type, and ground truth requirements
2. The orchestrator drives turn-taking between agents according to the configured conversation type (`one_to_one` or `dynamic`)
3. After every stakeholder turn, the analyst agent extracts requirements and issues from the message
4. The RE agent validates each extraction correcting errors and flagging missed items in a retry loop of up to three attempts
5. All messages, requirements, issues, and clarifications are written to the shared memory and persisted as JSON logs under `runs/`
6. After the simulation completes, the evaluator scores the run across seven research dimensions and saves a report to `results/`

---

## Architecture

```
scenarios/               YAML scenario configs
    ↓
src/
  main.py                CLI entry point loads scenario and starts simulation
  services/
    simulation_service.py  Core simulation runner (also called by API)
  orchestrator/          Drives agent turn-taking and conversation flow
  agents/                REAgent, UserAgent, HelperAgent (analyst), AgentFactory
  memory/                SharedMemory message store read/written by all agents
  logs/                  Logger persists run artefacts to disk
  llm/                   LLMFactory, provider enum, provider requirements.
  context/               LoadScenario YAML loader and CLI arg parser
  api/
    app.py               FastAPI application
    run.py               /runs list runs, load transcripts and artefacts
    initiate_simulation.py  /initiate start simulation, stream status via SSE
    results.py           /results list and retrieve evaluation reports
  evaluator.py           Seven-dimension evaluation engine
    ↓
runs/
  scenario_001/
    run_001/
      messages_log.json       Full conversation transcript
      requirements_log.json   Extracted and validated requirements
      issues_log.json         Detected issues with traceability links
      clarifications_log.json Clarification exchanges
      run_details.json        Timing, seed, status metadata
      config.yaml             Scenario config snapshot for reproducibility
    run_002/
    ...
    ↓
results/
  scenario_001_eval_1.json    Evaluation report (JSON)
  ...
    ↓
ui/                      React + TypeScript scenario builder, run viewer, evaluation dashboard
```

---

## Supported Providers

| Provider | Type | Free Tier | Notes |
|---|---|---|---|
| OpenAI | Cloud | No | GPT-4o, GPT-4o-mini, etc. Set `OPEN_AI_KEY` |
| Anthropic | Cloud | No | Claude 3.5 Sonnet, Haiku, etc. Set `ANTHROPIC_API_KEY` |
| Groq | Cloud | Yes | Fast inference, generous free tier. Set `GROQ_API_KEY` |
| Gemini | Cloud | Yes | Google models. Set `GEMINI_API_KEY` |
| Ollama | Local | N/A | Fully offline, no API key needed. Pull a model first. |

Each agent (RE, stakeholder, analyst) can be configured to use a different provider and model independently.

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- An API key for at least one cloud provider **or** [Ollama](https://ollama.com) installed locally for fully offline use

### 1. Clone the repository

```bash
git clone https://github.com/jakubsokal/SimOrch-Framework.git
cd SimOrch-Framework
```

### 2. Set up the Python environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r src/imports.txt
```

### 3. Configure environment variables

```bash
cp src/.env.example src/.env
```

Edit `src/.env` and add your key(s). The variable names must match exactly:

```env
# OpenAI
OPEN_AI_KEY=sk-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Groq (free tier at console.groq.com)
GROQ_API_KEY=gsk_...

# Google Gemini
GEMINI_API_KEY=...

# Ollama runs locally no key needed
# Install from https://ollama.com then: ollama pull llama3
```

### 4. Set up the UI

```bash
cd ui
npm install
```

### 5. Start the API and UI

Open two terminals from the project root:

```bash
# Terminal 1 FastAPI backend
python -m uvicorn src.api.app:app --reload

# Terminal 2 React frontend
npm --prefix ui run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 6. Run a simulation from the terminal (optional)

You can also run simulations directly without the UI:

```bash
python -m src.main --config scenario_001.yaml
```

The scenario file is loaded from the `scenarios/` directory. Logs are written to `runs/scenario_001/run_XXX/`.

---

## Scenarios

Scenarios are defined in YAML files inside the `scenarios/` directory. A scenario configures everything about a simulation agents, personas, LLM providers, conversation type, and ground truth requirements.

```yaml
scenario:
  id: scenario_001
  seed: 42                          # Seed for reproducibility
  scenario_name: Meeting Room Booking Elicitation
  description: >
    A structured elicitation session for a corporate meeting room booking system...
  domain: Corporate
  system_type: Booking System
  max_turns: 12
  conversation_type: dynamic        # one_to_one | dynamic

re_agents:
  - name: Requirement Engineer
    role: 1
    persona:
      experience_level: senior          # junior | intermediate | senior
      questioning_strategy: structured  # structured | exploratory
      probing_intensity: medium         # low | medium | high
      requirement_focus: functional     # functional | balanced | quality_oriented
      tone: formal                      # formal | neutral | friendly
    provider: openai
    model: gpt-4o-mini
    params:
      temperature: 0
      top_p: 1
      max_tokens: 512
    context_prompt: >
      You are an experienced Requirements Engineer conducting a structured
      elicitation interview...

user_agents:
  - name: Jamie
    role: 2
    persona:
      communication_style: concise      # cooperative | concise | vague | verbose | impatient
      domain_knowledge_level: high      # low | medium | high
      clarity_level: clear              # clear | partially_clear | unclear
      revelation_strategy: proactive    # reactive | proactive | reluctant
      revelation_rate: medium           # slow | medium | fast
    provider: openai
    model: gpt-4o-mini
    params:
      temperature: 0
      top_p: 1
      max_tokens: 512
    context_prompt: >
      You are Jamie, an office employee who books meeting rooms several times a week...

scenarioTruths:
  - id: R1
    type: FR
    statement: Users must be able to search for available meeting rooms by date, time, and capacity.
  - id: R2
    type: FR
    statement: Users must be able to book, modify, and cancel room reservations.
  - id: R6
    type: NFR
    statement: The system must be accessible via web and mobile.
```

See `scenarios/scenario_001.yaml` for a complete working example with multiple stakeholders.

---

## Conversation Types

| Type | Behaviour |
|---|---|
| `one_to_one` | RE agent and a single stakeholder alternate turns in strict sequence |
| `dynamic` | Orchestrator selects the next speaker based on the last message role, supporting multiple stakeholders in round-robin order |

---

## Persona System

Agent behaviour is controlled through structured persona configurations. Each dimension maps to a precise behavioural instruction injected into the agent's system prompt not a vague style hint but a specific rule governing how the agent must respond.

**RE Agent persona dimensions:**

| Dimension | Options |
|---|---|
| `experience_level` | `junior` `intermediate` `senior` |
| `questioning_strategy` | `structured` `exploratory` |
| `probing_intensity` | `low` `medium` `high` |
| `requirement_focus` | `functional` `balanced` `quality_oriented` |
| `tone` | `formal` `neutral` `friendly` |

**Stakeholder persona dimensions:**

| Dimension | Options |
|---|---|
| `communication_style` | `cooperative` `concise` `vague` `verbose` `impatient` |
| `domain_knowledge_level` | `low` `medium` `high` |
| `clarity_level` | `clear` `partially_clear` `unclear` |
| `revelation_strategy` | `reactive` `proactive` `reluctant` |
| `revelation_rate` | `slow` `medium` `fast` |

---

## Evaluation

Run evaluation across all runs of a scenario:

```bash
python -m src.evaluator <scenario_id>
# Example:
python -m src.evaluator 001
```

The evaluator reads all run folders under `runs/scenario_001/` and computes scores across seven dimensions. Results are saved to `results/scenario_001_eval_N.json` and can be viewed in the UI evaluation dashboard.

**Evaluation dimensions:**

| Dimension | What it measures |
|---|---|
| Feasibility | Completion rate and five behavioural validity checks (B1–B5) |
| Structural Reproducibility | Turn count and agent order consistency across runs |
| Semantic Reproducibility | SBERT embedding similarity of conversation content across runs |
| Requirement Content Reproducibility | Whether the same requirements were elicited across runs regardless of wording |
| Traceability | Structural and semantic links between extracted requirements and their source turns |
| Issues Traceability | Turn coverage and requirement linkage for detected issues |
| Ground Truth Coverage | Percentage of known ground truth requirements the simulation successfully elicited |

Semantic similarity uses `all-MiniLM-L6-v2` via `sentence-transformers` when available, falling back to TF-IDF cosine similarity, then `difflib` so the evaluator works even without GPU or heavy ML dependencies.

---

## API Endpoints

The FastAPI backend runs at `http://localhost:8000`.

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/initiate/` | Start a simulation with a scenario config payload |
| `GET` | `/initiate/stream` | SSE stream yields simulation status updates (running / completed / failed) |
| `GET` | `/runs/` | List all runs across all scenarios |
| `GET` | `/runs/scenarios` | List all predefined scenario YAML configs |
| `GET` | `/runs/{scenario_id}/{run_id}` | Load full run artefacts (transcript, requirements, issues, clarifications) |
| `GET` | `/results/` | List all evaluation reports |
| `GET` | `/results/{result_id}` | Load a specific evaluation report JSON |
| `GET` | `/health` | Health check |

---

## Using Ollama (Fully Local)

Install [Ollama](https://ollama.com) and pull a model:

```bash
ollama pull llama3
ollama pull mistral
ollama pull phi3
```

Set the provider in your scenario YAML:

```yaml
re_agents:
  - name: Requirement Engineer
    provider: ollama
    model: llama3
    ...
```

No API key, no internet connection, no usage costs. The simulation runs entirely on your machine. Useful for research environments with data privacy requirements.

---

## Run Output Structure

Each simulation run produces the following files under `runs/{scenario_id}/{run_id}/`:

| File | Contents |
|---|---|
| `messages_log.json` | Full conversation transcript with agent name, role, message, and turn number |
| `requirements_log.json` | Extracted and validated requirements with traceability links to source turns |
| `issues_log.json` | Detected issues (conflicts, ambiguities, risks) linked to requirements and turns |
| `clarifications_log.json` | Clarification exchanges between the RE agent and stakeholders |
| `run_details.json` | Timestamp, elapsed time, turn count, seed, and completion status |
| `config.yaml` | Snapshot of the scenario config used ensures the run is fully reproducible |

---

## Project Structure

```
SimOrch-Framework/
├── scenarios/              Scenario YAML configs
├── src/
│   ├── agents/             REAgent, UserAgent, HelperAgent, AgentFactory, PersonaBuilder
│   ├── orchestrator/       Conversation orchestration (one_to_one, dynamic)
│   ├── memory/             SharedMemory message and artefact store
│   ├── logs/               Logger run persistence
│   ├── llm/                LLMFactory, provider enum, requirements map
│   ├── context/            LoadScenario YAML loader and CLI arg parser
│   ├── services/           simulation_service.py core runner
│   ├── api/                FastAPI app, routers (runs, initiate, results)
│   ├── evaluator.py        Seven-dimension evaluation engine
│   ├── main.py             CLI entry point
│   └── .env.example        Environment variable template
├── ui/                     React + TypeScript frontend
├── runs/                   Simulation output (git-ignored)
└── results/                Evaluation reports (git-ignored)
```

---

## Contributing

Contributions are welcome. Please open an issue before submitting a large pull request so the approach can be discussed first.

1. Fork the repository
2. Create a feature branch from `dev`: `git checkout -b feature/your-feature`
3. Commit your changes with clear messages
4. Push and open a pull request against `dev`, not `main`

---

## Citation

If you use SimOrch in your research, please cite it:

```bibtex
@software{simorch2025,
  author = {Sokal, Jakub},
  title  = {SimOrch: Shared Memory Orchestration for Multi-Agent RE Simulation},
  year   = {2025},
  url    = {https://github.com/jakubsokal/SimOrch-Framework}
}
```

---

## License

This project is licensed under the MIT License see [LICENSE](LICENSE) for details.
