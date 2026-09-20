"""
Lead enrichment automator package.
Provides modular tools for lead intake, web lookup, Gemini AI enrichment,
and personalized email drafting.
"""

from enrichment.web_lookup import lookup_company
from enrichment.enrich import enrich_lead
from enrichment.email_drafter import draft_email

__all__ = [
    "lookup_company",
    "enrich_lead",
    "draft_email",
]
