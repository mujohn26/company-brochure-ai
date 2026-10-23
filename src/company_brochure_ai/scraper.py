from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
import requests
from urllib.parse import urljoin, urlparse


# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_html(url):
    """
    Download a page and return it as text, decoded as UTF-8.
    Passing a string (not bytes) to BeautifulSoup stops it from guessing
    the encoding and printing the "REPLACEMENT CHARACTER" warning.
    """
    response = requests.get(url, headers=headers, timeout=15)
    return response.content.decode("utf-8", errors="replace")


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    soup = BeautifulSoup(fetch_html(url), "html.parser")
    title = soup.title.string if soup.title and soup.title.string else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url):
    """
    Return the links on the website at the given url
    """
    soup = BeautifulSoup(fetch_html(url), "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    absolute_links = [urljoin(url, link) for link in links if link]
    return [
        link
        for link in absolute_links
        if urlparse(link).scheme in {"http", "https"}
    ]


def fetch_selenium_website_contents(url):
    """
    Return the title and contents of the website at the given url,
    rendered with a headless Chrome browser (for JavaScript-heavy or
    Cloudflare-protected sites); truncate to 2,000 characters
    """
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument(f"--user-agent={headers['User-Agent']}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(url)
        # Wait for the Cloudflare "Just a moment..." page to finish
        WebDriverWait(driver, 20).until(
            lambda d: "just a moment" not in d.title.lower()
        )
        body = driver.find_element(By.TAG_NAME, "body")
        title = driver.title or "No title found"
        return (title + "\n\n" + body.text)[:2_000]
    finally:
        driver.quit()