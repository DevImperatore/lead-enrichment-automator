"""
FastAPI service exposing lead enrichment and email drafting endpoints.
Enables direct integration with n8n HTTP Request nodes.
"""

import logging
import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from enrichment.enrich import enrich_lead
from enrichment.email_drafter import draft_email

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("lead_enrichment_service")

app = FastAPI(
    title="Lead Enrichment Service",
    description="Microservice for n8n lead intake, enrichment, and email drafting.",
    version="1.0.0"
)


class LeadInput(BaseModel):
    name: str = Field(..., max_length=120, description="Lead full name")
    company: str = Field(..., max_length=120, description="Company name")
    email: str = Field(..., max_length=120, description="Lead contact email")
    source: Optional[str] = Field("website", max_length=80, description="Lead source or channel")


class EnrichedResponse(BaseModel):
    lead: Dict[str, Any]
    enrichment: Dict[str, Any]
    email_draft: Dict[str, Any]


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "lead-enrichment-automator"}


@app.post("/enrich", response_model=EnrichedResponse)
def enrich_and_draft_endpoint(lead_data: LeadInput):
    """
    Receives incoming lead details, performs web lookup and AI enrichment,
    and generates a tailored email draft.
    """
    lead_dict = lead_data.model_dump()
    try:
        enrichment_data = enrich_lead(lead_dict)
        email_data = draft_email(lead_dict, enrichment_data)

        return {
            "lead": lead_dict,
            "enrichment": enrichment_data,
            "email_draft": email_data
        }
    except Exception as exc:
        logger.error("Enrichment processing failure: %s", str(exc), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing lead enrichment."
        )


def start_server():
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("enrichment.service:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    start_server()
