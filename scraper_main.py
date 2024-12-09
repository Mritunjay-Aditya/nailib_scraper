from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import re
from db_integration import DBHandler  # Assuming DBHandler is correctly defined
from datetime import datetime
import time  # Added for cool-down period

# MongoDB handler initialization
mongo_handler = DBHandler()

# Fetch page function
def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

# Scrape data function
def scrap(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else None
    subject_element = soup.find('h2', class_='file_sample__body__container__middle__cover__heading--small__gzm_v')
    subject = subject_element.get_text(" ", strip=True).split("'s")[0] if subject_element else None
    description = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None
    word_count = extract_word_count(soup)
    file_link = extract_file_link(soup)
    time_estimate = extract_timee(soup)
    sections = extract_sections(soup)

    created_at = updated_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "title": title,
        "subject": subject,
        "description": description,
        "sections": sections,
        "word_count": word_count,
        "time_estimate": time_estimate,
        "file_link": file_link,
        "publication_date": None,
        "page_url": url,
        "created_at": created_at,
        "updated_at": updated_at
    }

# Upsert data into MongoDB
def upsert(data):
    mongo_handler.collection.update_one(
        {"title": data["title"], "subject": data["subject"]},
        {"$set": data},
        upsert=True
    )
    print(f"Data for '{data['title']}' saved or updated successfully.")

# Extractors
def extract_word_count(soup):
    word_count_div = soup.find('div', class_='file_sample__body__container__middle__cover__list__nmVAV')
    if word_count_div:
        word_count_match = re.search(r'Word count:\s*([\d,]+)', word_count_div.get_text(strip=True))
        if word_count_match:
            return int(word_count_match.group(1).replace(',', ''))
    return None

def extract_file_link(soup):
    link = soup.find('a', href=re.compile(r'.*\.pdf$'))
    return link['href'] if link else None

def extract_timee(soup):
    time_estimate_div = soup.find('div', class_='file_sample__body__container__middle__cover__stat__RuwZ1')
    if time_estimate_div:
        time_text = time_estimate_div.find_all('div', class_='file_sample__body__container__middle__cover__stat__item__text__6umeQ')
        if time_text:
            return time_text[-1].get_text(strip=True).replace(' read', '')
    return None

def extract_sections(soup):
    sections = []
    toc_items = soup.find_all('ul', class_='file_toc__KmF9d')
    for toc_item in toc_items:
        link = toc_item.find('a', class_='file_toc__link__eLvZJ')
        if link:
            section_title = link.get_text(strip=True)
            if section_title not in sections:
                sections.append(section_title)
    return sections

# Scraping functions
def scrape_sample_page(url):
    html = fetch_page(url)
    if html:
        return scrap(html, url)
    return None

def scrape_and_save(url):
    data = scrape_sample_page(url)
    if data:
        upsert(data)
    else:
        print(f"Failed to scrape {url}")

# Scraping with Cool-Down Period
def scrape_from_file(file_path, cooldown_seconds=5):
    with open(file_path, "r") as file:
        links = file.readlines()
        for link in links:
            link = link.strip()  # Remove extra whitespace
            if link:
                scrape_and_save(link)
                print(f"Cooling down for {cooldown_seconds} seconds...")
                time.sleep(cooldown_seconds)  # Apply cooldown

# Main Execution
if __name__ == "__main__":
    print("Starting the scraping process...")
    scrape_from_file(r"data\EE_links.txt", cooldown_seconds=1)
    scrape_from_file(r"data\IA_links.txt", cooldown_seconds=1)
