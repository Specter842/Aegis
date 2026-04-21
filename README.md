# AEGIS

**A source-aware LLM firewall, enforcement proxy, and real-time security operations console.**

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OWASP LLM Top 10](https://img.shields.io/badge/OWASP-LLM_Top_10-brightgreen)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

AEGIS is a full-stack, production-ready LLM security firewall that acts as a bidirectional enforcement gateway between applications and LLM providers. By normalizing inputs, executing a multi-stage scanner pipeline, and actively mutating egress payloads, it provides deterministic control over LLM boundaries. Operators are equipped with total visibility through a premium real-time React console, allowing offline evaluation, incident forensics, and continuous tuning feedback.

---

## The Problem

Large Language Models interpret input as unbounded instructions, leaving them intrinsically vulnerable by default. Applications face direct injection attacks from malicious users and subtler indirect prompt injections buried within uploaded documents, hijacked URLs, or RAG context chunks. Compounding the risk is egress vulnerability; models frequently suffer from system prompt leakage or accidentally disclose sensitive API keys and PII back to unprivileged viewers. 

These risks map directly to the OWASP LLM Top 10 vulnerabilities (LLM01: Prompt Injections, LLM06: Sensitive Information Disclosure, LLM07: Insecure Plugin Design). Simple static keyword filters are insufficient—they inevitably block legitimate interactions while failing to detect encoded permutations or invisible unicode manipulation payloads, leaving enterprises with a false sense of security.

---

## What AEGIS Does

AEGIS operates as an active interception boundary natively bounding LLM traffic across both ingress and egress lifecycles dynamically.

<div align="center">
  <img src="assets/architecture.png" alt="AEGIS Prompt Secure & Processing Architecture">
</div>

---

## Core Capabilities

- **Bidirectional Enforcement Proxy:** Scans both inbound prompts and outbound model responses natively mapping provider abstractions (BaseProvider, OpenAIProvider).
- **Source-Aware Context Ingestion:** Actively fetches, parses, and chunks raw generic URLs and uploaded text documents asynchronously enforcing selective chunk boundaries without blocking entire healthy domains.
- **Canary Leak Detection:** Natively weaves high-entropy UUID tokens explicitly into protected system prompts mapping egressing context leaks and regurgitations structurally. 
- **Multi-Stage Scanner Pipeline:** Evaluates payloads synchronously through Regex limits, pre-compiled YARA rules, invisible Unicode analysis, and LLM Guard ML models concurrently.
- **Sensitive Output Mitigation:** Evaluates LLM responses stripping and aggressively isolating PII, Secrets, and sensitive hashes limiting outbound delivery exposures securely.
- **Real-Time Operator Console:** Driven by resilient WebSocket boundaries feeding into Attack Graphic node trees and chronological Incident Threat matrices robustly. 
- **Deterministic Policy Engine:** YAML-controlled thresholds mapping absolute explicit boundaries for `ALLOW`, `SANITIZE`, `CHALLENGE`, and `BLOCK` parameters.
- **Evaluation & Tuning Workflows:** Integrates completely decoupled offline testing pipelines matching labeled evaluations natively against persistent false positive/negative human-in-the-loop Database tables.

---

## Detection Engine

| Scanner | Type | Detects | Stage |
| :--- | :--- | :--- | :--- |
| **Unicode & Invisible Text** | Pre-process | ZWSP, BIDI overrides, obfuscated separators | 1 |
| **Encode & Base64 Traps** | Pre-process | Hex blobs, encoded injection permutations | 1 |
| **Token Limit Evaluator** | Structure | Exhaustion vectors hitting arbitrary input lengths | 2 |
| **Regex Scanner** | Static | Phrase overrides, role hijacking, general DAN escapes | 2 |
| **YARA Scanner** | Static | Explicit malicious payloads, extraction directives | 2 |
| **PromptInjection ML** | ML | Semantic prompt injection model classifications | 3 |
| **Secrets Engine ML** | ML | Exposed API keys, auth parameters, environment configs | 3 |
| **InvisibleText ML** | ML | Second-opinion evaluations on complex subversion tokens | 3 |

---

## Enforcement Model

**Trust Levels:**
AEGIS normalizes inputs into typed `ChannelText` objects dictating scanner aggressiveness:
* `Trusted`: Internal system configurations and developer instructions.
* `Semi_Trusted`: Authenticated local retrieval contexts.
* `Untrusted`: Raw End-User conversations, uploaded URLs, and external Docs.

**Pre-LLM Decision Bounds:**
* **ALLOW**: Very low risk, explicitly safe to forward.
* **SANITIZE**: Medium anomalies identified, strips malicious bounded sub-chunks dynamically forwarding cleaned strings securely.
* **CHALLENGE**: Ambiguous context; blocks natively unless an explicit End-User review boundary is passed. 
* **BLOCK**: High severity threshold passed, fully terminates API limits. 

**Post-LLM Egress Actions:**
* **ALLOW**: Clean response natively relayed to end consumers.
* **REDACT**: Specific secrets obfuscated securely mid-transit without destroying sentence completion contexts.
* **TRUNCATE**: Returns safe segments exactly up unto the violation bounding limit.
* **BLOCK**: Completely halts egress payload delivery bounding malicious provider data strictly to isolated offline system hashes.

---

## API Reference

| Method | Endpoint | Purpose |
| :--- | :--- | :--- |
| `POST` | `/v1/proxy/chat` | Main bidirectional enforcement loop forwarding chat bounds securely to OpenAI schemas. |
| `POST` | `/v1/analyze` | Legacy fallback mode evaluating raw prompts purely returning deterministic policy bounds. |
| `POST` | `/v1/documents/ingest` | Raw plaintext analysis boundary dynamically mapping overlapped chunk windows efficiently. |
| `POST` | `/v1/urls/ingest` | Native HTTPX fetches explicitly scrubbing DOM trees passing clean content into quarantines natively. |
| `GET` | `/v1/incidents` | Core retrieval arrays exporting trace limits and timeline historical bounds securely. |
| `POST` | `/v1/feedback` | Human validation bounds mapping explicit `[true_positive, false_negative]` keys to Trace IDs locally. |
| `WS` | `/ws/aegis` | Event-driven architecture publishing `SYSTEM_STATUS` and `ATTACK_DETECTED` outputs to React clients locally. |
| `GET` | `/health` | Static offline service test bounds validating backend liveness dynamically. |
| `GET` | `/ready` | Deep component polling bounds verifying Postgres, YARA, ML libraries, and network endpoints cleanly. |

---

## Persistence & Privacy Architecture

The entire dataset is driven securely via SQLAlchemy 2.x and AsyncPg boundaries mapped identically alongside robust Alembic migrations.

Most importantly: **Raw unsafe outputs are never stored natively in plain text payload representations.** 
The platform bounds all evaluations isolating only standard `safe_excerpts` (truncated explicitly down to 80 bytes), deterministic `output_hashes`, and mapped `block_reasons` restricting PII persistence inside analytical storage models securely.

---

## Evaluation and Tuning

AEGIS ships with an offline testing mechanism built into the `evals/` boundaries to measure deterministic success cleanly minimizing strict regression logic across system changes.

* **Benchmarks & Metrics**: Executable across `run_eval_suite.py` mapping directly against Precision, Recall, F1, FPR, and FNR structures bounding exactly against `attacks.jsonl` and `benign.jsonl` data sets.
* **Replay Execution**: Explicit script pipelines (`scripts/attack_replay.py`) ingest known DB instances natively testing permutations identically using explicit `--trace_id <UUID>` logic overrides.
* **Operator Validations**: Natively integrated across backend schemas dictating persistent state changes exactly identifying arbitrary reviews explicitly directly through `GET /v1/feedback/metrics`.

---

## Tech Stack

**Backend System:**
* Python + FastAPI + Pydantic v2
* SQLAlchemy 2.x (Async) + PostgreSQL + Alembic
* Python YARA Engine + LLM Guard ML models
* HTTPX + BeautifulSoup4 + Docker

**Frontend Console:**
* React + Vite (Event-driven operator boundaries)
* Framer Motion (State-aware UI/UX elements)
* Three.js & React Three Fiber (Data graph structures)

## Repository Structure

```text
AEGIS/
├── prompt-firewall/
│   ├── app/
│   │   ├── api/              # Routers (scan, proxy, documents, urls, ws, incidents, feedback)
│   │   ├── core/             # Config, logging, exceptions, constants
│   │   ├── db/               # PostgreSQL Models, async sessions, and repositories
│   │   ├── providers/        # LLM abstractions (BaseProvider, OpenAIProvider)
│   │   ├── scanners/         # Interfaces across Static and ML evaluation frameworks natively
│   │   ├── schemas/          # Hard Pydantic schema validation layers  
│   │   └── services/         # Normalizers, execution policies, Canaries and Egress integrations
│   ├── conf/                 # System yaml configurations defining threshold bounds safely 
│   ├── evals/                # Benchmarks targeting benign tests and known payload injections
│   ├── rules/                # Static YARA evaluation and complex regex logic constraints 
│   └── scripts/              # run_eval_suite.py and attack_replay.py execution architectures 
├── frontend/                 # Premium React/Vite operational security dashboard bounds 
└── backend/                  # Prototype references (inactive reference states safely quarantined)
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
