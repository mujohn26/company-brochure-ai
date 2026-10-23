"""Build the brochure prompt and stream the LLM's answer."""

from .clients import get_model
from .links import fetch_pages_and_relevant_links

MAX_PROMPT_CHARS = 5_000

BROCHURE_SYSTEM_PROMPT = """
You are an assistant that analyzes the contents of several pages of a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""


def get_brochure_user_prompt(company_name, url, model="OLLAMA"):
    user_prompt = (
        f"You are looking at a company called: {company_name}\n"
        "Here are the contents of its landing page and other relevant pages; "
        "use this information to build a short brochure of the company in markdown without code blocks.\n\n"
    )
    user_prompt += fetch_pages_and_relevant_links(url, model)
    return user_prompt[:MAX_PROMPT_CHARS]


def chunk_streams(stream):
    """Yield the growing response text so Gradio can display it as it streams."""
    result = ""
    for chunk in stream:
        if chunk.choices:
            result += chunk.choices[0].delta.content or ""
            yield result


def stream_brochure(company_name, url, model="GPT"):
    """Generate a brochure for the company, streaming the text as it's written."""
    client, model_name = get_model(model)
    messages = [
        {"role": "system", "content": BROCHURE_SYSTEM_PROMPT},
        {"role": "user", "content": get_brochure_user_prompt(company_name, url, model)},
    ]
    stream = client.chat.completions.create(model=model_name, messages=messages, stream=True)
    yield from chunk_streams(stream)