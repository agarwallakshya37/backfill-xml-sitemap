import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime
from urllib.parse import urlparse

def fetch_xml_and_parse(url):
    """Fetch XML content from a given URL and parse it."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Successfully fetched XML from: {url}")

        root = ET.fromstring(response.text)  # Parse XML once here
        return root
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        print(f"Error fetching or parsing {url}: {e}")
        return None

def is_valid_sitemap(loc_elem, lastmod_elem, start_date, end_date, content_filter):
    """Check if a sitemap entry is valid based on date and content filter."""
    if loc_elem is None:
        return False

    loc = loc_elem.text
    if lastmod_elem is not None:
        try:
            lastmod_date = datetime.fromisoformat(lastmod_elem.text.split("T")[0])
            if not (start_date <= lastmod_date <= end_date):
                return False
        except ValueError:
            print(f"Invalid date format in sitemap: {lastmod_elem.text}")
            return False

    if content_filter and not re.search(rf"\b{content_filter}\b", loc, re.IGNORECASE):
        return False

    return True

def extract_sitemap_links(root, start_date, end_date, content_filter):
    """Extract sitemap links filtered by lastmod date and content type."""
    if root is None:
        return {}

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap_links = {}

    for sitemap in root.findall(f".//{namespace}sitemap"):
        loc_elem = sitemap.find(f"{namespace}loc")
        lastmod_elem = sitemap.find(f"{namespace}lastmod")

        if not is_valid_sitemap(loc_elem, lastmod_elem, start_date, end_date, content_filter):
            continue

        loc = loc_elem.text
        print(f"Matched Sitemap: {loc}")
        sitemap_links[loc] = lastmod_elem.text if lastmod_elem is not None else None

        # Recursively process nested sitemaps
        nested_root = fetch_xml_and_parse(loc)
        if nested_root is not None:
            sitemap_links.update(extract_sitemap_links(nested_root, start_date, end_date, content_filter))

    return sitemap_links

def parse_sitemap(root, start_date, end_date):
    """Extract URLs from a sitemap within a date range."""
    if root is None:
        return [], 0

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = []

    total_doc_count = len(root.findall(f".//{namespace}url"))
    print(f"\nParsing Sitemap - Total Declared URLs: {total_doc_count}")

    for url_elem in root.findall(f".//{namespace}url"):
        loc_elem = url_elem.find(f"{namespace}loc")
        lastmod_elem = url_elem.find(f"{namespace}lastmod")

        if loc_elem is None:
            continue

        loc = loc_elem.text

        if lastmod_elem is not None:
            try:
                lastmod_date = datetime.fromisoformat(lastmod_elem.text.split("T")[0])
                if not (start_date <= lastmod_date <= end_date):
                    continue
            except ValueError:
                continue

        urls.append(loc)

    print(f"Extracted {len(urls)} URLs")
    return urls, total_doc_count

def main(sitemap_index_url, start_date, end_date, content_filter):
    """Main function to get all URLs from sitemaps within a date range."""
    print(f"\nFetching URLs from {start_date.date()} to {end_date.date()} with filter: {content_filter}")

    root = fetch_xml_and_parse(sitemap_index_url)
    if root is None:
        print("Error: Failed to fetch or parse the main XML sitemap.")
        return

    sitemaps = extract_sitemap_links(root, start_date, end_date, content_filter)
    all_urls_by_sitemap = {}

    for sitemap in sitemaps.keys():
        sitemap_root = fetch_xml_and_parse(sitemap)
        if sitemap_root is None:
            continue

        urls, total_count = parse_sitemap(sitemap_root, start_date, end_date)
        all_urls_by_sitemap[sitemap] = urls

        print(f"\nSitemap: {sitemap}")
        print(f"  → Total Documents Declared: {total_count}")
        print(f"  → Extracted Documents: {len(urls)}")

        if urls:
            print("  → Extracted URLs:(First 10)")
            for url in urls[:10]:
                print(f"    {url}")

    print("\nFinished processing.")

def validate_sitemap_url(sitemap_url):
    """Validate whether the provided URL is a sitemap index."""
    parsed_url = urlparse(sitemap_url)

    # Ensure it's a valid URL
    if not parsed_url.scheme or not parsed_url.netloc:
        print("Error: Invalid XML sitemap URL. Please enter a valid URL.")
        exit(1)

    # Ensure it's a sitemap index
    if not sitemap_url.endswith("sitemap_index.xml"):
        print("Error: The provided URL is not a sitemap index. Please enter a valid sitemap index URL.")
        exit(1)

if __name__ == "__main__":
    sitemap_index_url = input("Enter XML Sitemap Index URL: ").strip()
    validate_sitemap_url(sitemap_index_url)

    start_date_input = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date_input = input("Enter end date (YYYY-MM-DD): ").strip()
    content_filter = input("Enter content type filter (e.g., 'sitemap-posttype-post' or 'sitemap-post' or leave blank or anything else): ").strip()

    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    except ValueError:
        print("Error: Invalid date format. Please enter dates in YYYY-MM-DD format.")
        exit(1)

    if start_date > end_date:
        print("Error: Start date cannot be later than end date!")
        exit(1)

    main(sitemap_index_url, start_date, end_date, content_filter)