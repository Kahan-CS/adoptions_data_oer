import pandas as pd
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

def process_excel(file_path):
    """Reads input Excel file, processes links, and writes extracted titles to another sheet."""
    # Load workbook
    excel_file = pd.ExcelFile(file_path)
    
    if "Raw_input" not in excel_file.sheet_names:
        raise ValueError("Sheet 'Raw_input' not found in the Excel file.")
    
    df = pd.read_excel(excel_file, sheet_name="Raw_input")
    
    if "Links in CSV format" not in df.columns:
        raise ValueError("Column 'Links in CSV format' is missing.")
    
    link_titles_list = []
    
    for links in df["Links in CSV format"].fillna(""):
        link_set = {normalize_url(link) for link in str(links).split(", ") if link}
        link_titles = [link_title_mapping.get(link, fetch_title(link)) for link in link_set]
        link_titles_list.append(", ".join(link_titles))
    
    # Create DataFrame of the table adding the "Link Titles" column
    # df["Link Titles"] = link_titles_list
        
    # Write to "Extracted Titles" sheet
    # with pd.ExcelWriter(file_path, engine="openpyxl", mode="w", if_sheet_exists="replace") as writer:
    #     df.to_excel(writer, sheet_name="Extracted Titles", index=False)
        
    
    # Create DataFrame with only "Link Titles" column
    extracted_df = pd.DataFrame({"Link Titles": link_titles_list})
    
    # Write ONLY the "Link Titles" column to the "Extracted Titles" sheet
    with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        extracted_df.to_excel(writer, sheet_name="Extracted Titles", index=False)

# Example usage
process_excel("./data/Adoptions_Visuals_test.xlsx")
