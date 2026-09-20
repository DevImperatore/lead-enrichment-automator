# Lead Enrichment Automator

Automated B2B lead intake, web intelligence enrichment, and personalized email drafting system powered by n8n, Python, and Google Gemini API.

Built directly on real-world sales operations and bid pipeline workflows developed at Keystone Estimating Group.

---

## Executive Overview

In the commercial construction and estimating sector, sales conversion depends on response velocity and industry context. When general contractors, developers, or trade subcontractors submit an inquiry, generic automated replies fail to convert.

The `lead-enrichment-automator` captures inbound leads in real time via an HTTP webhook, automatically performs factual web research on the company, synthesizes business intelligence using Google Gemini API, and drafts high-context cold outreach emails tailored to construction estimating needs (bid deadlines, material takeoff accuracy, and estimating bandwidth).

---

## Architecture Flow

```text
[ Incoming Lead Webhook ]
            |
            v
[ n8n: Webhook Intake ] ---> [ n8n: Map Lead Fields ]
                                        |
                                        v
                            [ n8n: HTTP Request ]
                                        |
                                        v
                 [ Python Enrichment Service (FastAPI / CLI) ]
                 |-- 1. Web Lookup: DuckDuckGo Instant Data
                 |-- 2. Gemini Inference: Industry & Pain Points
                 +-- 3. Email Drafter: Keystone Estimating Pitch
                                        |
            +---------------------------+---------------------------+
            |                                                       |
            v (Optional: Disabled)                                  v
[ n8n: Create Gmail Draft ]                            [ n8n: Respond to Webhook ]
(Pending review in mailbox)                            (Return enriched JSON)
```

---

## Repository Components

| File / Directory | Type | Purpose |
|:---|:---|:---|
| `workflow/lead_enrichment.json` | n8n Workflow JSON | Exportable 5-node n8n workflow pipeline. |
| `enrichment/enrich.py` | Python Script / Module | Extracts lead data, invokes Gemini API, and infers industry attributes. |
| `enrichment/email_drafter.py` | Python Script / Module | Generates personalized outreach drafts grounded in Keystone Estimating context. |
| `enrichment/web_lookup.py` | Python Helper | DuckDuckGo search integration via HTTP requests for company background context. |
| `enrichment/service.py` | FastAPI Application | REST API serving `/enrich` endpoint for n8n HTTP Request node execution. |
| `enrichment/__init__.py` | Python Package | Public package exports for programmatic consumption. |
| `docs/workflow_diagram.md` | Documentation | Detailed step-by-step pipeline documentation and schema specifications. |
| `docs/setup_guide.md` | Documentation | Instructions to install, import, and test the workflow in local n8n. |
| `requirements.txt` | Dependency Manifest | Python packages required for execution and testing. |
| `.env.example` | Configuration | Template for environment variables and API keys. |

---

## Tech Stack

- **Workflow Orchestration**: n8n (v1 execution engine)
- **Programming Language**: Python 3.12+
- **Large Language Model**: Google Gemini API (`gemini-flash-latest` via `google-generativeai`)
- **API Framework**: FastAPI & Uvicorn
- **Web Intelligence**: DuckDuckGo Instant Answer / HTML Search via `requests`
- **Data Validation & Schemas**: Pydantic v2
- **Testing**: pytest

---

## Getting Started

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/DevImperatore/lead-enrichment-automator.git
cd lead-enrichment-automator
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy the example configuration file:

```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

```ini
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-flash-latest
PORT=8000
N8N_WEBHOOK_PATH=/webhook/lead-intake
```

### 3. Run Standalone Enrichment (CLI Mode)

You can run the enrichment engine directly in the terminal:

```bash
python -m enrichment.enrich
```

Or pass custom lead JSON:

```bash
python -m enrichment.enrich '{"name": "Robert Stone", "company": "Stone Mechanical Contractors", "email": "robert@stonemech.com", "source": "referral"}'
```

### 4. Run the Local Microservice

Start the FastAPI service to receive HTTP requests from n8n:

```bash
python -m enrichment.service
```

Health check:
```bash
curl http://localhost:8000/health
```

### 5. Import Workflow to n8n

1. Launch n8n locally (`npx n8n` or via Docker).
2. Go to **Workflows** > **Import from File**.
3. Select `workflow/lead_enrichment.json`.
4. The complete 5-node pipeline will be loaded and ready for execution.

---

## Sample Data

### Inbound Lead Request (POST /enrich)

```json
{
  "name": "Sarah Jenkins",
  "company": "Apex Drywall & Framing",
  "email": "sarah@apexdrywall.com",
  "source": "construction_network"
}
```

### Output Response

```json
{
  "lead": {
    "name": "Sarah Jenkins",
    "company": "Apex Drywall & Framing",
    "email": "sarah@apexdrywall.com",
    "source": "construction_network"
  },
  "enrichment": {
    "industry_guess": "Commercial Drywall & Framing Subcontractor",
    "company_size_guess": "mid",
    "pain_points": [
      "Heavy bid volume overwhelming internal estimating team",
      "Slow material pricing turnaround from suppliers",
      "Subcontractor bid scope gaps causing margin erosion"
    ],
    "personalization_notes": "Position Keystone as an on-demand overflow estimating desk for drywall bid packages."
  },
  "email_draft": {
    "subject": "Overflow estimating support for Apex Drywall",
    "body": "Hi Sarah,\n\nWith commercial drywall bid volumes fluctuating rapidly, keeping up with tight submission deadlines often strains internal estimating teams and delays getting competitive numbers out the door.\n\nKeystone Estimating Group acts as an on-demand overflow estimating desk for framing and drywall contractors. We deliver precise material takeoffs and complete, dependable bid packages quickly, enabling your team to capture more work without the burden of additional overhead.\n\nDo you have 10 to 15 minutes next week for a brief call to explore how we can support Apex's upcoming bid schedule?\n\nBest regards,\nThomas\nKeystone Estimating Group",
    "personalization_notes": "Positioned Keystone directly as an on-demand overflow estimating desk to address bid volume bottlenecks.",
    "status": "generated"
  }
}
```

---

## Domain Context: Keystone Estimating Group

This project translates field experience from Keystone Estimating Group into software automation:
- **Pain Point Mapping**: Construction contractors rarely need generic sales software; their existential challenge is estimating capacity on bid day.
- **Tone Calibration**: B2B outreach avoids generic corporate buzzwords and directly addresses material takeoffs, division CSI coding, and bid turnaround times.
- **Safety First**: Gmail draft creation is disabled by default, ensuring human-in-the-loop validation before real outreach emails are dispatched.

---

## License

MIT License
