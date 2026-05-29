import httpx
from bs4 import BeautifulSoup

# 1. Simulate the raw HTML response downloaded from the internet
# In a real scraper, this text is fetched using: response = httpx.get(url)
# response.text gives you this exact long, flat string with HTML tags and newlines
mock_html_response = """
<html>
    <body>
        <div class="book-box">
            <h3 class="title">Harry Potter</h3>
            <span class="price">$59.00</span>
        </div>
        <div class="book-box">
            <h3 class="title">The Lord of the Rings</h3>
            <span class="price">$68.00</span>
        </div>
    </body>
</html>
"""

print("=== 1. Simulating HTTPX Request Output ===")
# Show that the server initially gives us nothing but a plain Python string (str)
print(f"Data Type: {type(mock_html_response)}")
print(f"First 50 characters: {mock_html_response.strip()[:50]}...")


print("\n=== 2. Wrapping the String into a BeautifulSoup Object ===")
# This step is exactly what `return BeautifulSoup(response.text, "html.parser")` 
# does inside your advanced scraper wrapper function.
soup = BeautifulSoup(mock_html_response, "html.parser")
print(f"Data Type: {type(soup)}")


print("\n=== 3. Showing the Difference: Extracting the First Book Title ===")

# ❌ Approach A: Using pure string manipulation (The HTTPX-only way)
# You are forced to use hardcoded index searching or complex Regular Expressions.
# If the website structure changes even slightly (e.g., adding an extra space), this breaks instantly.
try:
    # Find where the title class starts, then offset by the length of the string marker
    start_idx = mock_html_response.find('class="title">') + len('class="title">')
    # Find the closing tag marker right after the title
    end_idx = mock_html_response.find('</h3>', start_idx)
    # Slice the string to extract the raw text
    title_via_str = mock_html_response[start_idx:end_idx]
    print(f"[Pure String Slicing] Success -> Title: {title_via_str}")
except Exception as e:
    print(f"[Pure String Slicing] Failed: {e}")

#  Approach B: Using the object navigation capabilities given by BeautifulSoup
# It builds a structured tree out of the string, letting you query it elegantly and precisely.
# "Find the <h3> tag with class 'title' inside the <div> tag with class 'book-box'"
first_book_title = soup.select_one("div.book-box h3.title").text
print(f"[BeautifulSoup Selection] Success -> Title: {first_book_title}")


print("\n=== 4. Ultimate Showdown: Extracting All Book Prices ===")
# Doing this with pure strings would require a complex loop counting characters for every <span>.
# With BeautifulSoup, you can grab all matching tags instantly as a clean Python list:
all_prices = [span.text for span in soup.select("span.price")]
print(f"Instantly fetched all prices: {all_prices}")