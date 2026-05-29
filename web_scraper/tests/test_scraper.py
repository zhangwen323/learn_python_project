"""Tests for scraper module — parsing logic only (no network)."""

from bs4 import BeautifulSoup
from web_scraper.scraper import parse_listing_page


SAMPLE_PAGE = """
<html><body>
<section>
  <ol class="row">
    <li>
      <article class="product_pod">
        <div class="image_container">
          <a href="catalogue/book_1/index.html">
            <img src="media/cache/book1.jpg" alt="Book One" />
          </a>
        </div>
        <p class="star-rating Three"></p>
        <h3><a href="catalogue/book_1/index.html" title="Book One">Book One</a></h3>
        <div class="product_price">
          <p class="price_color">£51.77</p>
          <p class="instock availability">In stock</p>
        </div>
      </article>
    </li>
    <li>
      <article class="product_pod">
        <div class="image_container">
          <img src="media/cache/book2.jpg" alt="Book Two" />
        </div>
        <p class="star-rating Five"></p>
        <h3><a href="catalogue/book_2/index.html" title="Book Two">Book Two</a></h3>
        <div class="product_price">
          <p class="price_color">£12.99</p>
          <p class="instock availability">In stock</p>
        </div>
      </article>
    </li>
  </ol>
</section>
</body></html>
"""


def test_parse_listing_extracts_title():
    soup = BeautifulSoup(SAMPLE_PAGE, "html.parser")
    books = parse_listing_page(soup)
    assert len(books) == 2
    assert books[0].title == "Book One"
    assert books[1].title == "Book Two"


def test_parse_listing_extracts_price():
    soup = BeautifulSoup(SAMPLE_PAGE, "html.parser")
    books = parse_listing_page(soup)
    assert books[0].price_gbp == "£51.77"
    assert books[1].price_gbp == "£12.99"


def test_parse_listing_extracts_rating():
    soup = BeautifulSoup(SAMPLE_PAGE, "html.parser")
    books = parse_listing_page(soup)
    assert books[0].rating_text == "Three"
    assert books[1].rating_text == "Five"


def test_parse_listing_extracts_availability():
    soup = BeautifulSoup(SAMPLE_PAGE, "html.parser")
    books = parse_listing_page(soup)
    assert all(b.availability == "In stock" for b in books)


def test_parse_listing_detail_url():
    soup = BeautifulSoup(SAMPLE_PAGE, "html.parser")
    books = parse_listing_page(soup)
    assert "book_1" in books[0].detail_url
    assert "book_2" in books[1].detail_url


def test_parse_empty_page():
    soup = BeautifulSoup("<html></html>", "html.parser")
    books = parse_listing_page(soup)
    assert books == []
