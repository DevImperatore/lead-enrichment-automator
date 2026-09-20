# Lead Enrichment Automator - Workflow Diagram & Architecture

This document outlines the step-by-step data pipeline for the `lead-enrichment-automator`. The workflow captures inbound sales leads via an HTTP webhook, enriches company data using web lookups and Google Gemini API, and prepares personalized cold outreach drafts based on Keystone Estimating Group construction workflows.

---

## High-Level Architecture Flowchart

```text
+-----------------------+
| Inbound Sales Lead    |
| (Web Form / Zapier)   |
+-----------+-----------+
            |
            v  POST /webhook/lead-intake
+-----------------------+
| Node 1: Webhook Intake|
+-----------+-----------+
            |
            v
+-----------------------+
| Node 2: Map Fields    | (Extract name, company, email, source)
+-----------+-----------+
            |
            v  POST http://localhost:8000/enrich
+-------------------------------------------------------------+
| Node 3: Python Enrichment Engine                            |
|                                                             |
|   1. web_lookup.py   -> DuckDuckGo Instant Answer / HTML    |
|   2. enrich.py       -> Gemini API (Industry & Pain Points) |
|   3. email_drafter.py-> Gemini API (Keystone Custom Draft)  |
+-----------------------------+-------------------------------+
                              |
              +---------------+---------------+
              |                               |
              v (Optional: Disabled)          v
+-----------------------------+   +---------------------------+
| Node 4: Gmail/SMTP Draft    |   | Node 5: Respond to Webhook|
| (Store draft in mailbox)    |   | (Return enriched JSON)    |
+-----------------------------+   +---------------------------+
```

---

## Step-by-Step Pipeline Table

| Step | Node Name | Node Type | Input Payload | Output Payload | Description |
|:---|:---|:---|:---|:---|:---|
| 1 | Webhook Intake | `n8n-nodes-base.webhook` | HTTP POST Body from landing page or CRM | Raw JSON payload with request headers | Listens on `/webhook/lead-intake` in webhook response mode. |
| 2 | Map Lead Fields | `n8n-nodes-base.set` | Output from Webhook Intake | Normalized object: `name`, `company`, `email`, `source` | Sanitizes field names and applies default fallbacks for missing values. |
| 3 | Call Python Enrichment | `n8n-nodes-base.httpRequest` | Normalized lead object | Complete enriched profile with LLM inference & email draft | Executes HTTP request to Python enrichment service (`localhost:8000/enrich`). |
| 4 | Create Gmail Draft (Optional) | `n8n-nodes-base.gmail` | Enriched lead + email draft | Gmail draft object with Draft ID | Creates a pending draft in Gmail without sending (disabled by default for human review). |
| 5 | Respond to Webhook | `n8n-nodes-base.respondToWebhook` | Full enrichment payload | HTTP 200 response with JSON body | Returns the structured enriched lead back to the original caller synchronously. |

---

## Data Schemas

### 1. Inbound Webhook Payload (Input)

```json
{
  "name": "David Miller",
  "company": "Apex Drywall & Framing",
  "email": "david.miller@apexdrywall.com",
  "source": "website_contact_form"
}
```

### 2. Intermediate Enriched Lead Schema

```json
{
  "industry_guess": "Commercial Drywall & Framing Subcontractor",
  "company_size_guess": "mid",
  "pain_points": [
    "Tight estimating bid deadlines and turnaround bottlenecks",
    "Inaccurate material takeoffs causing budget slippage",
    "Scarcity of experienced senior estimators for bid packages"
  ],
  "personalization_notes": "Position Keystone as an on-demand overflow estimating desk for commercial bid packages.",
  "web_context_snippet": "Apex Drywall & Framing specializes in commercial drywall, steel stud framing, and acoustical ceilings across commercial developments."
}
```

### 3. Generated Email Draft Schema

```json
{
  "subject": "Overflow estimating support for Apex Drywall",
  "body": "Hi David,\n\nWith commercial drywall bid volumes fluctuating rapidly, keeping up with tight submission deadlines often strains internal estimating teams and delays getting competitive numbers out the door.\n\nKeystone Estimating Group acts as an on-demand overflow estimating desk for framing and drywall contractors. We deliver precise material takeoffs and complete, dependable bid packages quickly, enabling your team to capture more work without the burden of additional overhead.\n\nDo you have 10 to 15 minutes next week for a brief call to explore how we can support Apex's upcoming bid schedule?\n\nBest regards,\nThomas\nKeystone Estimating Group",
  "personalization_notes": "Positioned Keystone directly as an on-demand overflow estimating desk to address bid volume bottlenecks specific to commercial drywall contractors.",
  "status": "generated"
}
```

### 4. Final Webhook Response Schema

```json
{
  "lead": {
    "name": "David Miller",
    "company": "Apex Drywall & Framing",
    "email": "david.miller@apexdrywall.com",
    "source": "website_contact_form"
  },
  "enrichment": {
    "industry_guess": "Commercial Drywall & Framing Subcontractor",
    "company_size_guess": "mid",
    "pain_points": [
      "Tight estimating bid deadlines and turnaround bottlenecks",
      "Inaccurate material takeoffs causing budget slippage",
      "Scarcity of experienced senior estimators for bid packages"
    ],
    "personalization_notes": "Position Keystone as an on-demand overflow estimating desk for commercial bid packages."
  },
  "email_draft": {
    "subject": "Overflow estimating support for Apex Drywall",
    "body": "Hi David,\n\nWith commercial drywall bid volumes fluctuating rapidly...",
    "personalization_notes": "Positioned Keystone directly as an on-demand overflow estimating desk..."
  }
}
```
