# AEGIS: Next-Gen Autonomous Security Kernel

## 1. Architecture Summary
AEGIS shifts the paradigm from strict traditional keyword "Firewall" filtering to a layered, model-aware bidirectional gateway. We utilize a pipeline consisting of:
- **Pre-LLM Prompt Normalizers:** Ensuring unicode subversion and evasion techniques are normalized securely.
- **Source-Aware Ingestion Pipelines:** Directly scanning parsed documents and URL chunks preventing Indirect Context Injection dynamically.
- **Secure Egress Proxying:** Rather than deploying simple drop functions, AEGIS dynamically edits (Redact/Truncation schemas) outgoing provider models and prevents exfiltration.
- **Data Minimization Constraints:** Storing completely evaluated representations rather than pure unencrypted payload payloads in persistent telemetry storage. 

## 2. Measurable Defense Profile (Evaluation Metrics)

Using rigorous JSONL testing mechanisms (e.g. `evals/run_eval_suite.py`), the suite is optimized strictly for **F1 Analysis**, monitoring exact bounds against:

*   **Precision**: Targeting minimal False Positives on complex prompt configurations (SOC2, HIPAA, and basic code questions).
*   **Recall**: Ensuring we successfully enforce strict context mappings dropping Canary Leaks entirely during data-extraction simulation tests.

## 3. The 3-Minute Demo Pitch

**[Opening — The Problem (30s)]**
"Every enterprise wants generative AI, but integrating it safely is terrifying. Traditional keyword firewalls block legitimate code snippets, miss advanced indirect injections, and most dangerously—fail to observe the model's actual egress. We've built AEGIS to solve exactly this."

**[The Solution & Demo — (90s)]**
*(Showcase the AEGIS Dashboard)*
"This is AEGIS. It operates seamlessly as a smart proxy API. Let me show you what happens when we attempt to inject a destructive payload... 
Watch the pipeline light up. Our pre-LLM gates just neutralized that context payload before tokens were wasted on the provider! 

But the real magic happens on egress. Many attacks rely on subtle model regurgitation. AEGIS natively weaves a high-entropy 'Canary Token' seamlessly into the LLM system prompt. 
*(Submit Output-Leak query)* 
If the LLM attempts to output that protected context, our `Output Gate` drops it instantly! The operator sees it on the dashboard safely as a 'Protected Context Leak'."

**[Operator Tooling & Close — (60s)]**
"This isn’t just a black box blocker. We built it for enterprise SOC teams. See the metrics graph and the True/False positive tuners directly in the UI? Analysts can immediately assess trace structures, playback evaluations, and submit real-time tuning feedback. 

AEGIS provides intent-aware security, robust indirect-injection quarantine, and an auditable API layer without compromising performance—turning Generative AI from a liability back into an asset."
