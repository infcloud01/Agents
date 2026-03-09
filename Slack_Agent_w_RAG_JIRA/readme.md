# Image Development RAG Slackbot

This project is an intelligent Slackbot designed to act as the manager of a team. It uses LangGraph and OpenAI to answer consumer questions by searching a local ChromaDB knowledge base (RAG). If a user reports a bug, requests a feature, or needs human intervention, the agent can automatically create a Jira support ticket.

The bot utilizes Slack Socket Mode, meaning it can run securely behind your firewall without needing a public HTTP endpoint. It also features thread-level memory, allowing it to maintain conversational context within individual Slack threads.

---

## Key Features

* **Retrieval-Augmented Generation (RAG):** Uses a LangChain `MultiQueryRetriever` and ChromaDB to fetch relevant company documentation and accurately answer user questions.
* **Automated Jira Ticketing:** Can extract summaries and descriptions from conversations to automatically generate Jira issues (Tasks) on behalf of users.
* **Conversational Memory:** Uses LangGraph's `MemorySaver` mapped to Slack Thread IDs, allowing the bot to remember previous messages in the same thread.
* **Automated Data Ingestion:** Includes a dedicated script to parse local PDFs, chunk the text, and embed the data into the vector database.
* **Linux/Chroma Compatibility:** Includes the `pysqlite3` workaround for seamless ChromaDB deployment on Linux environments.

---

## Prerequisites

Before running this bot, ensure you have the following:

* Python 3.9+ installed.
* A Slack Workspace with an App created, Socket Mode enabled, and the necessary Bot/App tokens.
* An OpenAI API account with billing enabled.
* A Jira Cloud account with an API token.

---

## Setup and Installation

**1. Clone the repository**

```bash
git clone <your-repository-url>
cd <your-repository-directory>

```

**2. Create a virtual environment and activate it**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

```

**3. Install the dependencies**

```bash
pip install -r requirements.txt

```

**4. Configure Environment Variables**
Create a `.env` file in the root directory of your project and populate it with your API keys (see the Environment Variables section below).

---

## Building the Knowledge Base

Before running the Slackbot, you need to populate the Chroma vector database with your company documentation.

1. Create a folder named `knowledge_base` in the root directory.
2. Drop your company documentation (PDF format) into the `knowledge_base` folder.
3. Run the ingestion script:

```bash
python ingest.py

```

This script will read the PDFs, split them into manageable 1,000-character chunks, generate embeddings using OpenAI's `text-embedding-3-small` model, and save the resulting database to `./chroma_db`.

---

## Running the Bot

Once your knowledge base is built, you can start the Slackbot:

```bash
python main.py

```

You should see `⚡️ Starting Agentic RAG Slackbot with LangGraph Memory...` in your terminal.

---

## Environment Variables

Your `.env` file must include the following variables for the agent and ingestion script to function correctly:

| Variable Name | Description |
| --- | --- |
| `SLACK_BOT_TOKEN` | Starts with `xoxb-`. Grants the bot permission to read/write messages. |
| `SLACK_APP_TOKEN` | Starts with `xapp-`. Required for Slack Socket Mode connections. |
| `OPENAI_API_KEY` | Your OpenAI API key for LLM and Embedding generation. |
| `JIRA_SERVER_URL` | The base URL for your Jira instance (e.g., `https://yourcompany.atlassian.net`). |
| `JIRA_USER_EMAIL` | The email address associated with your Jira API token. |
| `JIRA_API_TOKEN` | Your personal Jira API token. |
| `JIRA_PROJECT_KEY` | The short key for the Jira project where tickets should be created (e.g., `IMGDEV`). |

---

## Usage

Once the bot is running and invited to a Slack channel, simply mention it to start a conversation:

**`@YourBotName` How do I resize an image using our internal tools?**
The bot will trigger the `search_knowledge_base` tool, query the Chroma database, and reply in a thread with the documented answer.

**`@YourBotName` I'm getting a 500 error when I try to upload a PNG.**
The bot will recognize this as an issue, trigger the `create_support_ticket` tool, generate a Jira task, and return the Jira link to the user.

---

Would you like me to go ahead and write that `.gitignore` file for you now so you can ensure your `.env` and PDF files stay safe?
