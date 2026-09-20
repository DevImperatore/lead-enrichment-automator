# Setup and Deployment Guide

This guide explains how to deploy and configure the `lead-enrichment-automator` workflow in a local development environment with n8n and Python.

---

## Prerequisites

Ensure the following tools are installed on your host system:
1. **Python 3.10+**: Runtime for enrichment and LLM orchestration.
2. **Node.js 18+ or Docker**: Required for running n8n locally.
3. **Google Gemini API Key**: Obtainable from Google AI Studio.
4. **Git**: For version control.

---

## Step 1: Clone and Configure Python Environment

Navigate to the project directory:

```bash
cd "c:/Users/thoma/OneDrive/Escritorio/Workspace 3/02_PORTFOLIO/lead-enrichment-automator"
```

Create and activate a virtual environment:

```bash
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Create your local `.env` configuration from the template:

```bash
cp .env.example .env
```

Open `.env` and configure your credentials:

```ini
GOOGLE_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest
PORT=8000
N8N_WEBHOOK_PATH=/webhook/lead-intake
```

---

## Step 2: Start the Python Enrichment Microservice

Launch the FastAPI server that serves enrichment requests to n8n:

```bash
python -m enrichment.service
```

The service will start on `http://0.0.0.0:8000` with the following active endpoints:
- `GET /health`: Health verification endpoint.
- `POST /enrich`: Lead enrichment and email draft generator.

To verify the service is running, send a test health request:

```bash
curl -X GET http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "lead-enrichment-automator"}
```

---

## Step 3: Install and Start n8n

If n8n is not already installed, you can start it via npm or Docker:

### Option A: Local npm installation
```bash
npx n8n
```

### Option B: Docker container
```bash
docker run -it --rm \
  --name n8n \
  -p 5679:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

Open your browser and navigate to `http://localhost:5678` (or `http://localhost:5679` if running via Docker port mapping).

---

## Step 4: Import the Workflow into n8n

1. In the n8n web interface, click on **Workflows** in the left navigation sidebar.
2. Click the **Add Workflow** button in the top right corner.
3. Click the three dots menu (**...**) in the upper right header and select **Import from File**.
4. Select `workflow/lead_enrichment.json` from the repository:
   ```
   lead-enrichment-automator/workflow/lead_enrichment.json
   ```
5. The 5 pipeline nodes will appear on the canvas:
   - `Webhook Intake`
   - `Map Lead Fields`
   - `Call Python Enrichment`
   - `Create Gmail Draft (Optional)`
   - `Respond to Webhook`
6. Click **Save** in the upper right.

---

## Step 5: Configure and Activate Nodes

### 1. Webhook Intake Node
- Open the `Webhook Intake` node.
- Note the test webhook URL: `http://localhost:5678/webhook-test/lead-intake`.
- Note the production webhook URL: `http://localhost:5678/webhook/lead-intake`.

### 2. Call Python Enrichment Node
- If n8n runs directly on your host machine, the default target URL `http://localhost:8000/enrich` works out of the box.
- If n8n runs inside Docker, update the URL to `http://host.docker.internal:8000/enrich`.

### 3. Optional: Gmail Node
- The `Create Gmail Draft (Optional)` node is set to **Disabled** by default to prevent unwanted drafts.
- To enable automatic draft creation:
  1. Toggle node status from Disabled to Active.
  2. Create or connect an OAuth2 credential for Google Gmail in n8n.
  3. Ensure the `Draft` resource and `Create` operation are selected.

---

## Step 6: End-to-End Testing

With both n8n and the Python service running, trigger an inbound test lead via `curl`:

```bash
curl -X POST "http://localhost:5678/webhook-test/lead-intake" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marcus Vance",
    "company": "Vance Commercial Contracting",
    "email": "m.vance@vancecontracting.com",
    "source": "website_contact_form"
  }'
```

Expected Response:

```json
{
  "lead": {
    "name": "Marcus Vance",
    "company": "Vance Commercial Contracting",
    "email": "m.vance@vancecontracting.com",
    "source": "website_contact_form"
  },
  "enrichment": {
    "industry_guess": "Commercial General Contracting",
    "company_size_guess": "mid",
    "pain_points": [
      "Subcontractor bid scope gaps and coordination risks",
      "Estimating department turnaround times on bid days",
      "Material escalation forecasting and budget certainty"
    ],
    "personalization_notes": "Emphasize Keystone's pre-bid scope gap audits and 48-hour takeoff capabilities."
  },
  "email_draft": {
    "subject": "Estimating capacity and bid support for Vance Commercial",
    "body": "Hi Marcus,\n\nI noticed Vance Commercial Contracting has been active across commercial projects...",
    "personalization_notes": "Focused on subcontractor scope gap reduction and estimating turnaround speed.",
    "status": "generated"
  }
}
```

---

## Troubleshooting
 
### Custom Port Configuration
If port `8000` is already in use by another service on your machine, you can change the port in `.env`:
```ini
PORT=8080
```
Then update the URL parameter in n8n's `Call Python Enrichment` node to `http://localhost:8080/enrich`.

### DuckDuckGo Rate Limits
If high volume lookups trigger rate limits, `web_lookup.py` catches all network exceptions and returns an empty string without failing the enrichment pipeline. Gemini will continue enriching the lead based on company name and domain cues.
