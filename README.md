AI Social Media Marketing Agent
================================

This project is a starter **AI agent** that helps market your business on social media by:

- Generating posts for each of your services using an LLM (e.g. OpenAI)
- Adapting tone per platform (Instagram, Facebook, LinkedIn, X/Twitter)
- Providing clear hooks where you can plug in real social media APIs to publish automatically

> Important: This starter does **not** ship with production-ready API integrations for each platform, but it gives you a clean structure and the exact places to add real posting logic.

## 1. Setup

### 1.1. Create and activate a virtual environment (recommended)

On Windows PowerShell:

```bash
cd c:\Users\rajas\Downloads\ClaudeLocal
python -m venv .venv
.venv\Scripts\activate
```

### 1.2. Install dependencies

```bash
pip install -r requirements.txt
```

### 1.3. Configure environment variables

Create a file named `.env` in the project root:

```bash
OPENAI_API_KEY=your_openai_key_here
```

You can use any OpenAI-compatible provider; just ensure the key and model name in `social_agent/llm_client.py` are set correctly.

## 2. Describe your business

Edit `business_profile.json` to match your business:

- Business name and brand voice
- Target audience
- List of services (name, benefits, ideal customers, keywords)

The agent uses this file to generate on-brand social posts.

## 3. How the agent works

The core flow is:

1. Load `business_profile.json`.
2. For each service and platform, generate a platform-specific post (text, hashtags, image idea).
3. Call per-platform publishing hooks (currently placeholders) in `social_agent/platforms.py`.

You can run a single-shot generation and pseudo-posting to all platforms from the command line.

## 4. Running the agent

### 4.1. Generate and “post” once (console output)

```bash
python run_agent.py
```

This will:

- Load your business profile
- Generate posts for each configured platform
- Print what it would post (instead of calling real APIs)

## 5. Connecting real social media accounts

To actually post to real accounts, you need to:

1. Create developer apps on:
   - Meta for Developers (Facebook/Instagram)
   - X Developer Portal
   - LinkedIn Developer Portal
2. Implement the placeholder functions in `social_agent/platforms.py`:
   - Exchange the stored access tokens for API calls
   - Call the official APIs to publish content
3. Store access tokens securely (never commit them to Git or share them).

The code is structured so that you can add this logic without changing the agent’s planning and generation behavior.

## 6. Scheduling (optional)

For automatic posting on a schedule, you can:

- Use Windows Task Scheduler to run `python run_agent.py` at certain times, or
- Add a scheduler library like `schedule` or `APScheduler` and build a loop that runs the agent periodically.

This starter keeps scheduling simple so you can focus first on the generation quality and API connections.

