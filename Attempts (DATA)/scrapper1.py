import requests
from bs4 import BeautifulSoup

# Function to scrape attraction names from a page
def scrape_attraction_names(url):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    r = requests.get(url,headers=HEADERS)

    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup.prettify())

    # p=soup.findAll('div',class_='XfVdV o AIbhI')
    # print(p)

    div_tag = soup.findAll('div', class_='XfVdV o AIbhI')

    return div_tag

# Base URL
base_url = "https://www.tripadvisor.in/Attractions-g297685-Activities-oa{}-Varanasi_Varanasi_District_Uttar_Pradesh.html"

# Number of attractions per page
attractions_per_page = 30

# Number of pages (assuming 557 attractions)
total_attractions = 557
total_pages = 20

# List to store all attraction names
all_attraction_names = []

# Iterate over pages
for page_number in range(0, total_pages):
    url = base_url.format(page_number*30)
    attraction_names = scrape_attraction_names(url)
    all_attraction_names.extend(attraction_names)

# Print all attraction names
print(all_attraction_names)
