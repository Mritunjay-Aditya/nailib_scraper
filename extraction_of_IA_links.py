import requests
from bs4 import BeautifulSoup

def fetchAndSaveToFile(url, path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        links = soup.find_all('a', href=True)
        sample_links = [link['href'] for link in links if '/ia-sample/' in link['href']]
        with open(path, "w", encoding="utf-8") as f:
            for link in sample_links:
                f.write("https://nailib.com/"+link + "\n")
        
        print(f"Found and saved {len(sample_links)} links to {path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")


url = "https://nailib.com/ia-sample"
fetchAndSaveToFile(url, "data/IA_v2_links.txt")
