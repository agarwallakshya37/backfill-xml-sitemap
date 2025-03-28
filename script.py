import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urlparse

def fetch_xml(url):
    """Fetch XML content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error fetching {url}: {e}")

def extract_sitemap_links(xml_content, start_date, end_date, content_filter, base_domain):
    """Recursively extract sitemap links filtered by lastmod date, content type, and domain."""
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        raise ValueError("Invalid XML structure.")

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    sitemap_links = {}

    for sitemap in root.findall(f".//{namespace}sitemap"):
        loc_elem, lastmod_elem = sitemap.find(f"{namespace}loc"), sitemap.find(f"{namespace}lastmod")

        if loc_elem is None or urlparse(loc_elem.text).netloc != base_domain:
            continue  # Skip if no location or different domain

        lastmod_date = parse_lastmod_date(lastmod_elem, start_date, end_date)
        if lastmod_date is None:
            continue  # Skip if lastmod_date is outside range or invalid

        sitemap_links[loc_elem.text] = lastmod_date

        # Recursively process nested sitemaps
        add_nested_sitemaps(sitemap_links, loc_elem.text, start_date, end_date, content_filter, base_domain)

    return sitemap_links


def parse_lastmod_date(lastmod_elem, start_date, end_date):
    """Parse lastmod date and return only if within range."""
    if lastmod_elem is not None:
        try:
            lastmod_date = datetime.fromisoformat(lastmod_elem.text.split("T")[0])
            if start_date <= lastmod_date <= end_date:
                return lastmod_date
        except ValueError:
            return None  # Invalid date format
    return None


def add_nested_sitemaps(sitemap_links, loc, start_date, end_date, content_filter, base_domain):
    """Fetch and add nested sitemaps recursively."""
    try:
        nested_xml = fetch_xml(loc)
        if nested_xml:
            sitemap_links.update(extract_sitemap_links(nested_xml, start_date, end_date, content_filter, base_domain))
    except RuntimeError:
        pass  # Skip if fetching fails


def parse_sitemap(sitemap_url, start_date, end_date):
    """Extract URLs from a sitemap within a date range."""
    xml_content = fetch_xml(sitemap_url)
    if not xml_content:
        return [], 0

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        raise ValueError(f"Failed to parse XML for {sitemap_url}")

    namespace = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    urls = []
    total_doc_count = len(root.findall(f".//{namespace}url"))

    for url_elem in root.findall(f".//{namespace}url"):
        loc_elem = url_elem.find(f"{namespace}loc")
        lastmod_elem = url_elem.find(f"{namespace}lastmod")

        if loc_elem is None:
            continue

        loc = loc_elem.text
        if lastmod_elem is not None:
            try:
                lastmod_date = datetime.fromisoformat(lastmod_elem.text.split("T")[0])
                if lastmod_date < start_date or lastmod_date > end_date:
                    continue
            except ValueError:
                continue

        urls.append(loc)

    return urls, total_doc_count

def main(sitemap_index_url, start_date, end_date, content_filter):
    """Main function to fetch sitemaps and URLs based on filters."""
    base_domain = urlparse(sitemap_index_url).netloc
    xml_content = fetch_xml(sitemap_index_url)

    if not xml_content:
        raise RuntimeError("Failed to fetch the main XML sitemap.")

    sitemaps = extract_sitemap_links(xml_content, start_date, end_date, content_filter, base_domain)
    all_urls_by_sitemap = {}

    for sitemap in sitemaps.keys():
        urls, _ = parse_sitemap(sitemap, start_date, end_date)
        all_urls_by_sitemap[sitemap] = urls

    return sitemaps, all_urls_by_sitemap
