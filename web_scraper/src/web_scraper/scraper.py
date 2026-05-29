"""Scraper for books.toscrape.com — parse book listings, handle pagination and categories."""

import time
import random
import logging
from dataclasses import dataclass
from typing import Iterator

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "http://books.toscrape.com"
CATALOGUE_URL = f"{BASE_URL}/catalogue"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


@dataclass
class BookData:
    """Raw book data scraped from a listing page."""
    title: str
    price_gbp: str       # e.g. "£51.77" — cleaned later
    rating_text: str     # e.g. "Three"  — converted to int later
    availability: str    # e.g. "In stock"
    category: str
    image_url: str
    detail_url: str


def _random_ua() -> str:
    return random.choice(USER_AGENTS)


def _get_soup(url: str, max_retries: int = 3) -> BeautifulSoup:
    """Fetch a URL and return a BeautifulSoup object, with retries."""
    headers = {"User-Agent": _random_ua()}

    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.get(url, headers=headers, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            # The site declares ISO-8859-1 but content is actually UTF-8
            response.encoding = "utf-8"
            return BeautifulSoup(response.text, "html.parser")
        except httpx.HTTPError as e:
            logger.warning("Attempt %d/%d failed for %s: %s", attempt, max_retries, url, e)
            if attempt == max_retries:
                raise
            time.sleep(2 ** attempt)  # exponential backoff: 2s, 4s, 8s


def parse_listing_page(soup: BeautifulSoup, category: str = "") -> list[BookData]:
    """Parse a single book listing page and return a list of BookData."""
    books: list[BookData] = []

    for article in soup.select("article.product_pod"):
        # Title from <h3><a title="...">
        title_tag = article.select_one("h3 a")
        title = title_tag.get("title", "").strip() if title_tag else ""

        # Link to detail page
        detail_href = title_tag.get("href", "") if title_tag else ""
        if detail_href.startswith("../../../"):
            # Category page URLs are nested: ../../../book-name/index.html
            detail_href = detail_href.replace("../../../", f"{CATALOGUE_URL}/")
        else:
            detail_href = f"{CATALOGUE_URL}/{detail_href.lstrip('/')}"

        # Price from <p class="price_color">
        price_tag = article.select_one("p.price_color")
        price_gbp = price_tag.text.strip() if price_tag else ""

        # Rating from <p class="star-rating Three">
        rating_tag = article.select_one("p.star-rating")
        rating_text = ""
        if rating_tag:
            classes = rating_tag.get("class", [])
            rating_words = {"One": "One", "Two": "Two", "Three": "Three", "Four": "Four", "Five": "Five"}
            for cls in classes:
                if cls in rating_words:
                    rating_text = cls
                    break

        # Availability from <p class="instock availability">
        avail_tag = article.select_one("p.instock.availability")
        availability = avail_tag.text.strip() if avail_tag else ""

        # Image from <div class="image_container"><a><img src="...">
        img_tag = article.select_one("div.image_container img")
        img_src = img_tag.get("src", "") if img_tag else ""
        if img_src.startswith("../../../"):
            img_src = img_src.replace("../../../", f"{BASE_URL}/")
        elif img_src and not img_src.startswith("http"):
            img_src = f"{BASE_URL}/{img_src.lstrip('/')}"

        books.append(BookData(
            title=title,
            price_gbp=price_gbp,
            rating_text=rating_text,
            availability=availability,
            category=category,
            image_url=img_src,
            detail_url=detail_href,
        ))

    return books


def scrape_all_pages(
    start_url: str = f"{CATALOGUE_URL}/page-1.html",
    category: str = "",
    base_dir: str | None = None,
) -> list[BookData]:
    """Scrape all paginated listing pages starting from a URL.

    Follows the 'next' button to traverse pages. For main catalogue and
    category pages alike, the pagination hrefs are relative (e.g. 'page-2.html').
    """
    all_books: list[BookData] = []
    url = start_url
    page_num = 1

    while url:
        logger.info("Scraping page %d: %s", page_num, url)

        try:
            soup = _get_soup(url)
        except httpx.HTTPError:
            break

        books = parse_listing_page(soup, category=category)
        if not books:
            break

        all_books.extend(books)
        logger.info("  Found %d books on this page (total: %d)", len(books), len(all_books))

        # Follow the 'next' link if present
        next_btn = soup.select_one("li.next a")
        if not next_btn:
            break

        next_href = next_btn.get("href", "")
        if not next_href:
            break

        # Resolve relative URL against current page
        url = str(httpx.URL(url).join(httpx.URL(next_href)))

        page_num += 1
        time.sleep(0.5 + random.random() * 0.5)

    return all_books


def get_categories() -> list[tuple[str, str]]:
    """Return a list of (category_name, category_url) tuples from the sidebar."""
    soup = _get_soup(f"{BASE_URL}/index.html")
    categories: list[tuple[str, str]] = []

    # The sidebar has <ul class="nav nav-list"> → <li> → <ul> → <li> → <a>
    sidebar = soup.select_one("ul.nav-list")
    if not sidebar:
        return categories

    for link in sidebar.select("li ul li a"):
        name = link.text.strip()
        href = link.get("href", "")
        # href like: catalogue/category/books/travel_2/index.html
        if href:
            # Strip leading / and trailing index.html, build full URL
            href = href.strip()
            if href.startswith("/"):
                href = href[1:]
            # Build absolute URL
            url = f"{BASE_URL}/{href}"
            categories.append((name, url))

    return categories


def scrape_all_books(limit: int | None = None) -> list[BookData]:
    """Scrape the entire site: all categories, all pages. Returns all books."""
    all_books: list[BookData] = []

    categories = get_categories()
    logger.info("Found %d categories", len(categories))

    for cat_name, cat_url in categories:
        logger.info("Category: %s — %s", cat_name, cat_url)
        books = scrape_all_pages(start_url=cat_url, category=cat_name)
        all_books.extend(books)
        logger.info("  Total books in '%s': %d", cat_name, len(books))

        if limit and len(all_books) >= limit:
            all_books = all_books[:limit]
            break

    return all_books
