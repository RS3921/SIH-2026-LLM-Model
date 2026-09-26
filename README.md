# SOVEREIGN — SIH26117 prototype

An on-premise, agentic AI workbench for the SIH 2026 problem statement **SIH26117: Sovereign On-Premise Agentic AI Workbench using Open-Weight Multimodal LLMs for Confidential Industrial Work** (MRPL, Smart Automation).

## Run locally

Requirements: Node.js 20+, Python 3.10+, Ollama, and Python packages `pypdf`, `pypdfium2`, `Pillow`, `python-docx`, and `openpyxl`. These must already be installed or supplied from an offline wheelhouse; there are no npm dependencies.

1. Provision Ollama, the Python packages, and approved text/vision model files using your offline installation media or internal software repository. The app never downloads models.
2. To register an offline GGUF model with Ollama, place the file and a `Modelfile` together. For example, the `Modelfile` can contain `FROM ./assistant.gguf`; run `ollama create assistant -f Modelfile`. For vision, provision an Ollama-compatible multimodal model too. Model import depends on a compatible GGUF and its required files.
3. In this directory, start the local model service (`ollama serve` if it is not already running).
4. Start the app: `npm start`.
5. Open `http://127.0.0.1:4173`.

After local provisioning, normal app use does not require internet access: the workbench binds to `127.0.0.1`, calls only Ollama at `127.0.0.1:11434`, uses no cloud API, telemetry, remote fonts, or CDN assets, and has no npm dependencies. Ollama's documented [GGUF import flow](https://ollama.com/blog/improved-performance-and-model-support-with-gguf) uses a local `Modelfile` and `ollama create`.

## What the prototype does

- Detects installed Ollama models and routes document, coding, reasoning and image tasks, with per-task model overrides.
- Extracts text from PDF, DOCX, XLSX, TXT, Markdown, CSV, JSON and LOG files; stores local files and chunk indexes under `data/knowledge`.
- Sends attached PNG/JPEG/WebP images, or up to the first four pages of an uploaded PDF, to a local vision model when the user asks a visual question. Rendered page images remain in memory and are not written as separate files.
- Uses BM25-style lexical ranking over local chunks and lets users expand exact evidence excerpts behind answer citations.
- Runs a bounded model/tool loop with local knowledge search, safe arithmetic, and generated Word approval notes or CSV files.
- Writes a capped local JSONL audit trail of document and agent-tool events, displays recent activity, and restores the trail and indexed files after restarting.
- Generates a per-browser P-256 device key locally. The non-exportable private key stays in IndexedDB; the prototype shows a short public-key fingerprint so a future company identity service can enroll and recognize the device.

## Company identity and device trust

The intended production flow is **company identity first, device continuity second**. Authenticate employees against the company's existing on-prem identity provider (for example, an intranet OIDC/SAML service); do not create a second employee password database in this workbench. Keep only a short-lived, minimal local cache such as an opaque employee subject, tenant, required role claims, and expiry. The authoritative employee record and access decisions remain on the company server. Refresh or revoke access when the company server is reachable; define a company-approved short offline grace period if disconnected operation is needed.

The prototype's **Identity & device** panel creates a unique browser key pair and retains its non-exportable private key locally. A company identity integration would enroll the public key after employee login, issue a fresh challenge on later sessions, and verify the signed challenge before marking that device as recognized. A different key means a new browser key/device enrollment; a matching key is only continuity evidence. It does not prove the same person is present, and browser storage is not hardware-backed. Production should use company-approved MFA and, where available, hardware-backed WebAuthn/device attestation, with key revocation, rotation, server-side role checks, and rate limits.

This is currently a **UI and local key-generation prototype**, not employee authentication: no company identity provider is connected, employee records are not stored, and API routes are not protected by user or role checks. The app listens only on loopback, so this feature must be integrated with the company's intranet identity and deployment architecture before multiple employees or shared servers use it.

## Prototype boundaries

This is a local-first proof of concept, not a certified air-gap or production security boundary. The document index uses lexical ranking; there is no vector database yet. Scanned PDF pages can be inspected by the local vision model, but their text is not OCR-extracted into the search index, and only the first four pages are available per PDF. Dense P&ID interpretation, handwriting extraction, code execution, policy enforcement, role-based access, encryption at rest, and network-isolation attestation remain future work. The model router uses task keywords and installed model names rather than quality feedback. For a strict air-gapped deployment, provision runtimes and approved model files in advance, disconnect the host, then independently verify its egress controls.

Files and generated deliverables are local to `data/knowledge` and `data/deliverables`. Use the context panel to remove an indexed source file. Generated DOCX/CSV outputs can be deleted from `data/deliverables`.
