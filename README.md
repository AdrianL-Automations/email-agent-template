# Self-Hosted AI Email Agent (Llama 3.2 + LangGraph)
> **Architectural Showcase** | Status: `Demo / Skeleton`

A privacy-first, self-hosted AI agent designed to run **locally** on agency infrastructure. It processes incoming emails, categorizes them using Chain-of-Thought logic, and drafts context-aware replies without data ever leaving your server.

---

### Why Self-Hosted?
* **100% Privacy:** Uses local LLMs (Llama 3.2). No data is sent to OpenAI.
* **GDPR Compliant:** Infrastructure resides entirely within your EU/On-Prem environment.
* **Zero API Costs:** Runs on your own hardware (or VPS) using Ollama.

### Architecture

This system uses a **State Graph** architecture to prevent "AI Hallucinations." The agent must pass through strict logic gates before drafting a reply.

```mermaid
graph LR
    A[Inbound Email] --> B(Categorizer Node);
    B --> C{Decision Logic};
    C -- URGENT --> D[Alert Human];
    C -- SPAM --> E[Ignore];
    C -- LEAD --> F(Draft Reply + Calendar Link);
    C -- OTHER --> G(Standard Acknowledge);
    F --> H[Guardrails Check];
    H --> I[Save to Drafts];