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
