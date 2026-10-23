"""Use an LLM to pick the links on a website that are worth reading for a brochure."""

import json
from urllib.parse import urljoin

import requests

from .clients import get_model
from .scraper import fetch_website_contents, fetch_website_links

LINKS_SYSTEM_PROMPT = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""


def get_links_user_prompt(url):
    links = fetch_website_links(url)
    return (
        f"Here is the list of links on the website {url} -\n"
        "Please decide which of these are relevant web links for a brochure about the company, "
        "respond with the full https URL in JSON format.\n"
        "Do not include Terms of Service, Privacy, email links.\n\n"
        "Links (some might be relative links):\n"
        + "\n".join(links)
    )


def _normalize_links(data, base_url):
    """
    Turn whatever the model returned into a clean list of {"type", "url"} dicts.
    Small local models don't always follow the JSON format exactly, e.g. they
    return plain URL strings instead of objects.
    """
    items = data.get("links", []) if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []

    links = []
    for item in items:
        if isinstance(item, dict):
            link_type, link_url = item.get("type", "page"), item.get("url")
        elif isinstance(item, str):
            link_type, link_url = "page", item
        else:
            continue
        if link_url:
            links.append({"type": link_type, "url": urljoin(base_url, link_url)})
    return links


def select_relevant_links(url, model="OLLAMA"):
    """Ask the LLM which links on the page are relevant for a brochure."""
    client, model_name = get_model(model)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": LINKS_SYSTEM_PROMPT},
            {"role": "user", "content": get_links_user_prompt(url)},
        ],
        response_format={"type": "json_object"},
    )
    try:
        data = json.loads(response.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        print("Model returned invalid JSON; continuing with the landing page only.")
        return []
    return _normalize_links(data, url)


def fetch_pages_and_relevant_links(url, model="OLLAMA"):
    """Return the landing page text plus the text of every relevant linked page."""
    contents = fetch_website_contents(url)
    result = f"## Landing Page:\n\n{contents}\n## Relevant links:\n"

    for link in select_relevant_links(url, model):
        try:
            page = fetch_website_contents(link["url"])
        except requests.exceptions.RequestException as e:
            print(f"Skipping {link['url']}: {e.__class__.__name__}")
            continue
        result += f"\n\n### Link: {link['type']}\n{page}"
    return result