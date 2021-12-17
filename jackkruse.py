import os
import re
import time
import random
import typing
import hashlib

import pdfkit
import requests
from bs4 import BeautifulSoup

ATTEMPTS: int = 100
ROOT: str = "https://jackkruse.com/blogindex/page/{page}/"


def save(filename: str, data: str) -> None:
    """Saves `data` into a cache file in the /tmp called `filename`."""
    path: str = os.path.join(os.sep, "tmp", filename)
    with open(path, "w") as file_handler:
        file_handler.write(data)


def get(filename: str) -> str:
    """Loads data from a cache file in the /tmp called `filename`, if it exists."""
    path: str = os.path.join(os.sep, "tmp", filename)
    if not os.path.isfile(path):
        return ""
    with open(path, "r") as file_handler:
        return file_handler.read()


def load(url: str) -> str:
    """Downloads an HTML from the `url` if it doesn't exist in the cache."""
    filename: str = hashlib.md5(url.encode("utf-8")).hexdigest() + ".html"
    cached: str = get(filename)
    if cached:
        return cached
    print(f"URL: {filename}")
    response: str = requests.get(url)
    assert response.status_code == 200
    save(filename, response.text)
    time.sleep(random.uniform(0, 5))
    return response.text


def pdf(url: str) -> str:
    """Exports `url` as a PDF if it doesn't exist in the cache."""
    print(f"CRAWL: {url}")
    if not url:
        return
    url: str = url.strip() + "?print=print"
    filename: str = (
        hashlib.md5(url.encode("utf-8")).hexdigest() + ".pdf"
    )
    assert url
    assert filename
    if not os.path.isdir("pdf"):
        os.mkdir("pdf")
    path: str = os.path.join("pdf", filename)
    if not os.path.isfile(path):
        for i in range(ATTEMPTS):
            print(f"PDF: {path}")
            try:
                pdfkit.from_url(url, path)
                break
            except Exception as error:
                print(f"ERROR: {error}")
                time.sleep(2 * i)
                continue


def links(html: str) -> typing.Generator[str, None, None]:
    """Returns a list of links found in the `html` string."""
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", text=re.compile("Read More")):
        url = link.get("href")
        if url and url.startswith("http"):
            yield url


if __name__ == "__main__":
    for page in range(1, 100):
        url = ROOT.format(page=page)
        link = None
        for link in links(load(url)):
            pdf(link)
        if link is None:
            break
    print("Crawled successfully!")
