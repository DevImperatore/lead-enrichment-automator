"""
Web lookup module for lead enrichment.
Fetches summary snippets for company names using DuckDuckGo via HTTP requests.
"""

from typing import Optional
from urllib.parse import quote_plus
import requests


def lookup_company(company_name: str, timeout: int = 5) -> str:
    """
    Searches DuckDuckGo for the company name and returns a text snippet.
    If the request fails or no result is found, returns an empty string.

    Args:
        company_name: Name of the company to query.
        timeout: Request timeout in seconds (default: 5).

    Returns:
        str: Summary text snippet or empty string on failure.
    """
    if not company_name or not company_name.strip():
        return ""

    sanitized_name = company_name.strip()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }

    # First attempt: DuckDuckGo Instant Answer API
    try:
        encoded_query = quote_plus(sanitized_name)
        api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(api_url, headers=headers, timeout=timeout)

        if response.status_code in (200, 202):
            data = response.json()
            # Check primary abstract
            abstract = data.get("AbstractText") or data.get("Abstract")
            if abstract and isinstance(abstract, str) and abstract.strip():
                return abstract.strip()

            # Check related topics
            related = data.get("RelatedTopics", [])
            if related and isinstance(related, list):
                for item in related:
                    if isinstance(item, dict) and "Text" in item and item["Text"].strip():
                        return item["Text"].strip()
    except Exception:
        pass

    # Second attempt: DuckDuckGo HTML search endpoint
    try:
        html_url = f"https://html.duckduckgo.com/html/?q={quote_plus(sanitized_name)}"
        response = requests.get(html_url, headers=headers, timeout=timeout)
        if response.status_code == 200 and response.text:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            snippet_elem = soup.find("a", class_="result__snippet")
            if snippet_elem and snippet_elem.text:
                return snippet_elem.text.strip()
            # Generic snippet fallback
            first_body = soup.find("div", class_="result__snippet")
            if first_body and first_body.text:
                return first_body.text.strip()
    except Exception:
        pass

    return ""


if __name__ == "__main__":
    import sys

    query = sys.argv[1] if len(sys.argv) > 1 else "Keystone Estimating Group"
    result = lookup_company(query)
    print(f"Company: {query}")
    print(f"Snippet: {result if result else 'No snippet found'}")
