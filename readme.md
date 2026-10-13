# NOVA — Next-Generation Voice AI Assistant

NOVA is a high-performance, executive voice AI assistant designed for real-time natural speech interaction, multi-modal document intelligence, web research, and deep Microsoft 365 / WorkIQ MCP enterprise integration.

Built with a native **Quantum Neural Core** audio-reactive HUD, NOVA provides ultra-low latency conversational responses using Gemini Live bidirectional streaming while operating within a safe, non-intrusive sandbox architecture.

---

## 🌟 Key Capabilities

### 🎙️ 1. Ultra-Low Latency Voice Assistant
- **Bidirectional Audio Streaming**: Direct real-time streaming input and output with Google Gemini Live.
- **Natural Interruptibility**: Barge-in speech detection lets you speak over the assistant at any time to redirect conversations seamlessly.
- **Multiple Neural Voices**: Switch between prebuilt expressive voices (*Charon*, *Puck*, *Kore*, *Fenrir*, *Aoede*).

### 🌌 2. Quantum Neural Core Visualizer
- **Custom Vector Graphics**: 60 FPS hardware-accelerated HUD rendering concentric quantum orbitals, floating particle nodes, and radial frequency waveforms.
- **Audio-Reactive States**: Visualizer dynamically transforms state across `IDLE`, `LISTENING`, `THINKING`, and `SPEAKING` with live frequency reactivity.

### 🏢 3. Microsoft 365 & WorkIQ Enterprise Integration
- **Microsoft Teams**: Send messages to channels and direct chats; review recent channel conversations and threads.
- **Microsoft Outlook**: Compose, review, and send emails; search inbox messages with natural language queries.
- **Microsoft Calendar**: Check upcoming appointments, retrieve daily agendas, and schedule new meetings.
- **WorkIQ MCP**: Enterprise knowledge retrieval via the Model Context Protocol (MCP) server for company files, confluence, and internal docs.

### 📄 4. Document Intelligence & Q&A
- **Universal Format Ingestion**: Analyze PDFs, Word documents (`.docx`), presentations (`.pptx`), spreadsheets (`.csv`, `.xlsx`), and text/code files.
- **Contextual Question-Answering**: Ask complex questions about multi-page documents, summarize reports, or extract structured data tables directly into conversation.

### 🌐 5. Web Search & Browser Navigation
- **Live Web Research**: Instant query search and summarization using DuckDuckGo.
- **Autonomous Browser Automation**: Extract page content, navigate links, take page screenshots, and inspect dynamic web apps via Playwright.

### 🧠 6. Persistent Local Memory
- **Long-Term Recall**: Learns user preferences, project details, and important facts over time.
- **Transparent Local Storage**: Memory stays entirely on your machine (`memory/long_term.json`) with full inspection and deletion controls in the UI.

### 🛡️ 7. Safe Executive Architecture
- **Zero OS Intrusiveness**: Does not execute unvetted terminal commands, take over keyboard/mouse, or tamper with system files.

---

## 🚀 Getting Started

### Prerequisites
- **Python**: Version 3.11, 3.12, or 3.13
- **Operating System**: macOS, Windows 10/11, or Linux
- **Gemini API Key**: Free or paid key from [Google AI Studio](https://aistudio.google.com/)

### Installation

1. **Clone or Download the Repository**:
   ```bash
   cd nova
   ```

2. **Create and Activate a Virtual Environment** (Recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   python setup.py
   ```
   *Alternatively:*
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` in the project directory, then fill in your keys.
   The template includes the required model lists; keep them or edit them for
   models supported by your account. On Windows PowerShell:
   ```powershell
   Copy-Item .env.example .env
   ```
   Do not overwrite an existing configured `.env`. Example credential settings:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Microsoft 365 (Optional / Fallback Sandbox Available)
   MICROSOFT_CLIENT_ID=your_azure_client_id_here
   MICROSOFT_CLIENT_SECRET=your_azure_client_secret_here
   MICROSOFT_TENANT_ID=common
   
   # WorkIQ MCP Enterprise Search
   WORKIQ_MCP_SERVER_URL=http://localhost:5005/mcp
   WORKIQ_API_KEY=your_workiq_mcp_api_key_here
   ```
   API credentials and model IDs are read exclusively from `.env`.
   Restart NOVA after editing it and check the app's connection status.
   A handshake timeout alone does not mean the key is invalid.

   `.env`, machine-specific settings, private assistant memory, virtual
   environments and caches are excluded from Git. Each clone must configure
   its own credentials; do not upload these private files.

5. **Launch NOVA**:
   ```bash
   python main.py
   ```

### Model selection in .env

Model IDs are runtime settings, not a commented inventory. Edit `.env` and
restart NOVA to apply changes. There are no hardcoded model-ID fallbacks:
missing or empty required settings report a configuration error.

| Setting | Purpose |
| --- | --- |
| `GEMINI_LIVE_MODELS` | Ordered voice-conversation models, primary first |
| `GEMINI_FAST_MODELS` | Ordered classification/extraction models |
| `GEMINI_SMART_MODELS` | Ordered reasoning/document/image-analysis models |
| `GEMINI_SEARCH_MODELS` | Ordered grounded-search REST models |

Gemini lists are comma-separated. `live` in FAST/SMART means a separate side
session using the current conversation model; it is not a model ID and is not
allowed in SEARCH or LIVE lists. Use compatible audio models for LIVE and REST
models with grounding support for SEARCH. Existing default selections and
fallback order are preserved in `.env`; you can remove or reorder fallbacks.

The app uses Gemini exclusively for speech understanding, answers and speech
output. There are no alternative local conversation engines or wake-word
downloads. It listens whenever connected and unmuted; optional push-to-talk
still limits microphone streaming to when the key is held.

Gemini uses `GEMINI_API_KEY`; Microsoft/WorkIQ credentials also come only from
`.env`. Credential forms save to `.env`, not JSON. JSON still stores UI preferences
such as the Gemini prebuilt voice picker, audio devices and feature toggles.

### Desktop-only networking

The app does not start the phone/remote dashboard, listen on ports 8000/8001,
or request administrator access to change firewall rules or network profiles.
Normal Gemini voice and text use outbound HTTPS and secure WebSockets to
`generativelanguage.googleapis.com` on TCP port 443; no inbound firewall rule
is needed.

On Windows, startup reads the Windows-configured proxy (including automatic
PAC configuration) for Gemini and uses it for HTTPS and secure WebSockets.
This read-only lookup runs without administrator access and does not modify
Windows settings. Explicit proxy settings and proxy bypass rules are preserved;
automatically detected values apply only to the current process and are
resolved again on the next launch, so switching Wi-Fi does not persist an
office proxy. Restart the app after changing networks.

If office access still fails, ask IT whether that endpoint and secure WebSocket
connections are permitted or require proxy authentication. If IT supplies an
explicit proxy URL, configure `HTTPS_PROXY` as directed by IT before launching.
Do not disable the firewall or TLS certificate verification.

### Responsive voice input

Voice interruption checks sustained microphone speech against playback echo
before stopping a reply, and retains the detected opening audio. Headphones
improve separation; noisy rooms can require longer detection.

This installation disables `proactive_audio` so Gemini does not intentionally
ignore questions as background conversation. Speech detection uses high start
and end sensitivity, 200 ms prefix padding, and 550 ms silence before ending
a question. These settings are stored in `config/api_keys.json`; restart after
changing them. Nearby speech may now trigger replies. Network and model
processing still add delay; responses are not instantaneous.

### Direct document processing

Uploaded documents use the original `file_processor` extraction and direct
Gemini analysis. There is no automatic embedding, indexing, or vector database.
The existing summarize, extract_text, analyze and conversion actions remain
available. Extracted text sent to Gemini is subject to the existing per-format
preview limits, so answers may not cover an entire large document.
Only upload documents you are authorized to send to Google.

---

## ⚙️ Configuration & Microsoft 365 Setup

### Microsoft Graph API Setup
To connect real Microsoft 365 accounts:
1. Navigate to the [Microsoft Entra Admin Center](https://entra.microsoft.com/) or Azure Portal.
2. Register a new application under **App registrations**.
3. Under **API permissions**, add Delegated permissions for Microsoft Graph:
   - `User.Read`
   - `Mail.Read`, `Mail.Send`
   - `Calendars.ReadWrite`
   - `Chat.ReadWrite`, `ChatMessage.Send`
4. Copy the **Client ID**, generate a **Client Secret**, and paste them into your `.env` file.
*(Note: If left unconfigured, NOVA automatically runs Microsoft operations in a safe simulated sandbox mode for immediate testing).*

### WorkIQ MCP Server Setup
NOVA can query any MCP server compliant with the WorkIQ schema:
- Set `WORKIQ_MCP_SERVER_URL` in `.env` (e.g. `http://localhost:5005/mcp`).
- NOVA handles authentication via Bearer token using `WORKIQ_API_KEY`.

---

## 📁 Project Structure

```
nova/
├── actions/                   # Permitted tool implementations
│   ├── browser_control.py     # Playwright web navigation & inspection
│   ├── file_processor.py      # PDF, DOCX, CSV, PPTX text extraction & Q&A
│   ├── microsoft_calendar.py  # Meeting scheduling and agenda queries
│   ├── microsoft_outlook.py   # Email composition, inbox search & delivery
│   ├── microsoft_teams.py     # Channel and direct chat messaging
│   ├── microsoft_workiq.py    # Enterprise intelligence & WorkIQ MCP search
│   ├── send_message.py        # Direct dispatch via Teams, Email & Webhooks
│   └── web_search.py          # Real-time search engine integration
├── config/                    # Application icons and settings
├── core/                      # Assistant engine and UI components
│   ├── audio_devices.py       # Audio hardware routing
│   ├── microsoft_client.py    # Microsoft Graph & WorkIQ MCP connector
│   ├── prompt.txt             # System prompt & behavioral protocol
│   ├── qt_compat.py           # Transparent PySide6 / PyQt6 cross-compat layer
│   └── visualizer.py          # Quantum Neural Core vector animation engine
├── memory/                    # Persistent long-term memory engine
├── .env.example               # Template environment configuration
├── main.py                    # Application entrypoint & Gemini Live pipeline
├── requirements.txt           # Python dependency specifications
├── setup.py                   # Automated setup utility
└── ui.py                      # Desktop HUD window and drawer controls
```
