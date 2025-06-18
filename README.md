# PentAiA – Pentest AI Agent

PentAiA is a secure, AI-assisted pentesting platform that allows security professionals to automate reconnaissance and vulnerability scanning workflows using local and remote tools. The platform leverages a local FastAPI server to orchestrate tools like Nmap, SQLMap, WhatWeb, and optionally BurpSuite/Nexpose—via CLI, Web UI, or LLM integration (e.g., ChatGPT).

## Key Features

- Modular tool execution (via FastAPI)
- Local-only or remote execution via Kali VM
- Natural language-driven interface (LLM optional)
- CLI and Web UI support
- Secure input handling and logging

## Getting Started

1. Clone the repo
2. Activate the virtualenv
3. Run the FastAPI server
4. Start issuing commands via CLI or WebUI (optional)

# Requirements

## Functional

- LLM Orchestration via OpenAI (ChatGPT), Claude, or local model
- Tool Integrations:
  - Core: `nmap`, `sqlmap`, `whatweb`, `wpscan`
  - Optional: BurpSuite Pro API, Rapid7 Nexpose API
- JSON-RPC-like API over FastAPI
- Input validation and sanitization
- Background tasks and result tracking
- Interfaces: CLI (primary), optional Web UI

## Non-Functional

- Runs on Ubuntu 24.04.2 LTS
- Tools isolated on Kali Linux VM
- Secure communication (via HTTP or SSH)
- Logs and audits all execution
- Single-user MVP; modular architecture for expansion
