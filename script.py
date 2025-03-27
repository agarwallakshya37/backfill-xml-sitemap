import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime

def fetch_xml(url):
    """Fetch XML content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_sitemap_links(xml_content, start_date, end_date, content_filter):
    """Extract sitemap links filtered by lastmod date and content type."""
    root = ET.fromstring(xml_content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

    sitemap_links = {}

    for smap in root.findall(f".//{namespace}sitemap"):
        loc = smap.find(f"{namespace}loc").text
        lastmod_elem = smap.find(f"{namespace}lastmod")

        # Filter by lastmod date if available
        if lastmod_elem is not None:
            lastmod_text = lastmod_elem.text
            try:
                lastmod_date = datetime.fromisoformat(lastmod_text.split("T")[0])  # Extract date
            except ValueError:
                print(f"Skipping invalid date format in sitemap: {lastmod_text}")
                continue

            if lastmod_date < start_date or lastmod_date > end_date:
                continue

        if content_filter and not re.search(rf"\b{content_filter}\b", loc, re.IGNORECASE):
            continue

        sitemap_links[loc] = 0  # Initialize count to 0

    print("\nFiltered Sitemap Links:")
    for link in sitemap_links.keys():
        print(link)

    return sitemap_links

def parse_sitemap_index(sitemap_url, start_date, end_date, content_filter):
    """Extract sitemap URLs from the index, filtered by lastmod date and content type."""
    xml_content = fetch_xml(sitemap_url)
    if not xml_content:
        return {}

    return extract_sitemap_links(xml_content, start_date, end_date, content_filter)

def parse_sitemap(sitemap_url, start_date, end_date):
    """Extract URLs from a sitemap within a date range and compare with declared count."""
    xml_content = fetch_xml(sitemap_url)
    if not xml_content:
        return [], 0  # Return empty list and 0 count

    root = ET.fromstring(xml_content)
    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = []

    total_doc_count = len(root.findall(f".//{namespace}url"))  # Count <url> elements

    for url_elem in root.findall(f".//{namespace}url"):
        loc = url_elem.find(f"{namespace}loc").text
        lastmod_elem = url_elem.find(f"{namespace}lastmod")

        if lastmod_elem is not None:
            lastmod_text = lastmod_elem.text
            try:
                lastmod_date = datetime.fromisoformat(lastmod_text.split("T")[0])  # Extract date only
            except ValueError:
                print(f"Skipping invalid lastmod format in URL: {lastmod_text}")
                continue

            if lastmod_date < start_date or lastmod_date > end_date:
                continue

        urls.append(loc)

    return urls, total_doc_count

def main(start_date, end_date, content_filter,sitemap_index_url):
    """Main function to get all URLs from sitemaps within a date range."""
    sitemaps = parse_sitemap_index(sitemap_index_url, start_date, end_date, content_filter)

    all_urls_by_sitemap = {}

    for sitemap in sitemaps.keys():
        urls, total_count = parse_sitemap(sitemap, start_date, end_date)
        sitemaps[sitemap] = total_count  # Store the total count
        all_urls_by_sitemap[sitemap] = urls

    return sitemaps, all_urls_by_sitemap

if __name__ == "__main__":
    sitemap_index_url = input("Enter XML Sitemap URL: ").strip()
    start_date_input = input("Enter start date (YYYY-MM-DD): ").strip()
    end_date_input = input("Enter end date (YYYY-MM-DD): ").strip()
    content_filter = input("Enter content type filter (e.g., 'sitemap-posttype-post' or 'sitemap-post' or leave blank or anything else): ").strip()

    try:
        start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
    except ValueError:
        print("Invalid date format. Please enter dates in YYYY-MM-DD format.")
        exit(1)

    content_regex = content_filter if content_filter else None

    print(f"\nFetching URLs from {start_date.date()} to {end_date.date()} with filter: {content_filter}\n")

    sitemaps, all_urls_by_sitemap = main(start_date, end_date, content_regex, sitemap_index_url)

    for sitemap, total_count in sitemaps.items():
        extracted_count = len(all_urls_by_sitemap[sitemap])
        print(f"\nSitemap: {sitemap}")
        print(f"  → Total Documents Declared: {total_count}")
        print(f"  → Extracted Documents: {extracted_count}")

        print("  → Extracted URLs:")
        for url in all_urls_by_sitemap[sitemap]:
            print(f"    {url}")

    print("\nFinished processing.")