# 🚀 AI Terminal Inbox

A powerful, terminal-based AI email assistant that connects directly to your local classic Microsoft Outlook and uses **Oracle GenAI** (via LangChain OCI) to summarize threads, auto-draft replies, and manage your inbox.

By utilizing Windows COM automation, this tool completely bypasses the need for complex Microsoft Graph API OAuth setups or enterprise IT approvals. It operates entirely locally, utilizing your already-authenticated Windows Outlook session.

## ✨ Features

* **Zero-Config Outlook Integration:** Connects to your local Outlook Inbox using `pywin32`. No Graph API tokens required.
* **Corporate-Compliant AI:** Uses Oracle Cloud Infrastructure (OCI) GenAI, ensuring your data stays within enterprise-approved boundaries.
* **Rich Terminal UI:** Beautiful, color-coded terminal interface built with `rich`.
* **Smart Summarization:** Instantly generate bulleted summaries of long, messy email chains.
* **Auto-Drafting:** Let the AI draft contextual replies, or provide custom instructions for a tailored response.
* **Non-Destructive Execution:** All AI-generated replies are saved directly to your Outlook **Drafts** folder for final human review. Nothing is sent automatically.
* **Automated Read Receipts:** Automatically marks processed emails as "Read" to keep your inbox clean.
* **Custom Signatures:** Automatically injects your professional signature into all AI-generated drafts.

## 📋 Prerequisites

1.  **Windows OS** (COM automation is Windows-exclusive).
2.  **Microsoft Outlook (Classic)** installed and running. *(Note: The "New Outlook" web-wrapper is not supported).*
3.  **Oracle Cloud Infrastructure (OCI)** account with GenAI services enabled.
4.  **Python 3.8+** installed.

## 🛠️ Setup & Installation

**1. Clone the repository**

```bash
git clone https://github.com/infcloud01/Agents.git
cd Agents/Outlook_Agent
```

**2. Install Dependencies**
Install the required Python packages using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

**3. Configure your OCI Credentials**
Ensure your local machine is authenticated with Oracle Cloud. This script defaults to using your standard OCI config file located at `~/.oci/config`.

**4. Set up your Environment Variables**
Create a `.env` file in the root directory of the project and add your specific OCI GenAI configuration:

```env
# .env
OCI_COMPARTMENT_ID="ocid1.compartment.oc1..YOUR_COMPARTMENT_OCID_HERE"
OCI_SERVICE_ENDPOINT="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
OCI_MODEL_ID="cohere.command-r-08-2024"
```
*⚠️ **IMPORTANT:** Never commit your `.env` file to version control. Ensure it is listed in your `.gitignore`.*

**5. Customize your Signature**
Open `outlook_terminal.py` and locate the `MY_SIGNATURE` variable at the top of the script. Update it with your personal details.

## 🚀 Usage

Ensure your desktop Outlook application is open and running in the background. Open your terminal and run:

```bash
python outlook_terminal.py
```

### The Main Menu
For each email, you will be presented with the following options:
* `[a] Auto-draft`: The AI reads the entire thread and drafts a logical, polite response automatically.
* `[c] Custom`: Provide a quick "gist" (e.g., "Tell them I approve the budget"), and the AI will draft the professional version.
* `[s] Summarize`: Generates a quick bulleted summary of the thread without skipping the email.
* `[i] Ignore`: Skips the current email and moves to the next one.
* `[q] Quit`: Exits the terminal application.

### The Draft Review Menu
If you generate a draft, you will enter a sub-menu to review the AI's work:
* `[s] Save`: Injects your signature, saves the draft to your Outlook Drafts folder, and marks the original email as read.
* `[r] Regenerate`: Discards the current draft and asks the AI to try again.
* `[d] Discard`: Trashes the draft and returns you to the Main Menu for that email.

## 🔒 Security & Privacy

This script was designed with enterprise security in mind:
* It does **not** use undocumented APIs or scrape web interfaces.
* It utilizes official Oracle GenAI SDKs to comply with standard corporate Data Loss Prevention (DLP) policies.
* It strictly operates in a "Draft-Only" mode to prevent accidental hallucinated emails from being sent to colleagues.
