import csv
import urllib.parse
import requests
from bs4 import BeautifulSoup

def normalize_url(url):
    """Removes tracking parameters and normalizes a URL."""
    parsed_url = urllib.parse.urlparse(url)
    cleaned_url = urllib.parse.urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return cleaned_url

# Predefined mapping of links to titles
link_title_mapping = {
    "https://ecampusontario.pressbooks.pub/hospitalunitadministration/": "Hospital Unit Administration",
    "https://stuconestogacon.sharepoint.com.mcas.ms/sites/Open_Learning_CC/SitePages/New-OER--Spanish-Workbook.aspx": "New OER - Spanish Workbook",
    "https://ecampusontario.pressbooks.pub/storiesofhopevol1/": "Stories of Hope Vol. 1",
    "https://openlibrary.ecampusontario.ca/item-details/#/3fe51733-9c82-433c-82c3-ee3f254e98a5": "Business Math : A Step-by-Step Handbook Abridged",
    "https://ecampusontario.pressbooks.pub/medicalterminology/": "Building a Medical Terminology Foundation"
}

def fetch_title(url):
    """Fetches the title of a webpage if not found in the predefined mapping."""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "Unknown Title"
        return title
    except requests.RequestException:
        return "Unknown Title"

def process_csv(input_file, output_file):
    """Reads input CSV, processes links, and writes output CSV with added title field."""
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile, delimiter='\t')
        fieldnames = reader.fieldnames + ["Link Titles"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter='\t')
        
        writer.writeheader()
        for row in reader:
            links = row["Links in CSV format"].split(", ") if row["Links in CSV format"] else []
            
            # Normalize and deduplicate links
            unique_links = {normalize_url(link) for link in links}
            
            # Get associated titles (fetch if not in predefined map)
            link_titles = [link_title_mapping.get(link, fetch_title(link)) for link in unique_links]
            
            # Add to row and write to output
            row["Links in CSV format"] = ", ".join(unique_links)  # Overwrite with cleaned links
            row["Link Titles"] = ", ".join(link_titles)
            writer.writerow(row)

# usage
process_csv("input_data.tsv", "output_data.tsv")
