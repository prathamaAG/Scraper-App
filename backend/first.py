import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import math
from datetime import datetime, timezone
from random import randint
from IPython.display import clear_output
clear_output(wait=True)
import random
from flask_socketio import SocketIO, emit
from flask import Flask, Response, request
from flask_cors import CORS
import json
from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

if os.name == 'posix':
    from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Function to determine the OS and set up Edge options
def get_browser():
    options = Options()
    options.add_argument("--disable-gpu")  # Disable GPU
    options.add_argument("--no-sandbox")  # Bypass OS security
    options.add_argument("--disable-software-rasterizer")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Helps avoid detection

    # Initialize Edge browser
    if os.name == 'nt':  # Windows
        edge_driver_path = './msedgedriver.exe'
        if not os.path.exists(edge_driver_path):
            raise FileNotFoundError(f"Edge WebDriver not found at {edge_driver_path}")
        
        service = Service(edge_driver_path)
    else:  # macOS/Linux
        service = Service(EdgeChromiumDriverManager().install())

    browser = webdriver.Edge(service=service, options=options)
    return browser

# Define the path to the dedicated folder
output_folder = os.path.join(os.path.expanduser("~"), "Downloads", "scraper_outputs")

# Create the folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
# result = None

@app.route('/firstScraper', methods=['POST'])
def scraper1():
    emit_progress(0)
    data = request.json
    headers = data.get('headers')
    attractionCount = data.get('attractionCount')
    fetched_link = data.get('urls')
    result = first_scraper(headers, fetched_link, attractionCount)
    # return result
    csv_data = result.to_csv(index=False)
    
    # Set response headers to indicate CSV content
    headers = {
        "Content-Disposition": "attachment; filename=data.csv",
        "Content-Type": "text/csv",
    }
    
    # Return CSV data as a response
    return Response(csv_data, headers=headers)

@app.route('/scraper1name', methods=['POST'])
def nameOfScraper():
    emit_progress(100)
    data = request.json
    headers = data.get('headers')
    fetched_link = data.get('urls')
    result = name_of_city(headers, fetched_link)
    return result

@app.route('/secondScraper', methods=['POST'])
def scraper2():
    emit_progress(0)
    data = request.json
    headers = data.get('headers')
    attractionCount = data.get('attractionCount')
    base_url = data.get('urls')
    result, img_result = second_scraper(headers, base_url, attractionCount)
    # return result
    csv_data1 = result.to_csv(index=False)
    csv_data2 = img_result.to_csv(index=False)
    
    # # Set response headers to indicate CSV content
    # headers = {
    #     "Content-Disposition": "attachment; filename=data1.csv",
    #     "Content-Type": "text/csv",
    # }
    
    # # Return CSV data as a response
    # return Response(csv_data1, headers=headers)
    response_data = {
        'reviews_csv': csv_data1,
        'images_csv': csv_data2
    }
    
    return jsonify(response_data)
    
@app.route('/scraper2name', methods=['POST'])
def nameForScraper2():
    emit_progress(100)
    data = request.json
    headers = data.get('headers')
    base_url = data.get('urls')
    result1 = second_scraper_name(headers, base_url)
    return result1

#if os.name == 'nt':
#    CHROME_DRIVER_PATH = r"C:\\Users\\Harsh\\Downloads\\chromedriver-win64\\chromedriver-win64"
#    os.environ['PATH'] += f";{CHROME_DRIVER_PATH}"  # Append to PATH
#else:
#    options = Options()
#    options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Adjust as needed    
#    service = Service(ChromeDriverManager().install())

# Endpoint to initiate scraping
@app.route('/scrape_reviews', methods=['POST'])
def scrape_reviews():
    data = request.json
    site_link = data.get('link')

    if not site_link:
        return jsonify({"error": "No link provided"}), 400

    try:
        reviews,location = get_google_reviews(site_link)
        if not reviews:
            return jsonify({"error": "No reviews found or failed to scrape"}), 500

        # Save reviews to CSV
        output_file = 'google_reviews.csv'
        df = pd.DataFrame(reviews)
        df.to_csv(os.path.join(output_folder, f"{location}.csv"), index=False)

        return jsonify({"message": "Scraping completed successfully", "file": output_file}), 200
    except Exception as e:
        print(f"Scraping Error: {e}")
        return jsonify({"error": "An error occurred during scraping"}), 500



def try_extract(extraction_method, retries=2, default_value=None):
    """
    Tries to extract a value using the provided extraction method, up to retries times.
    If extraction fails, returns the default_value.
    """
    attempt = 0
    while attempt < retries:
        try:
            return extraction_method()  # Try the extraction method
        except Exception as e:
#            print(f"Error on attempt {attempt + 1}")
            # print(e)
            attempt += 1
    return default_value  # Return default value if both attempts fail

def clean_filename(location_name):
    cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', location_name)  # Remove special characters
    cleaned_name = re.sub(r'\s+', '_', cleaned_name.strip())  # Replace spaces with underscores
    return cleaned_name

# Main Scraping Function
def get_google_reviews(site_link):

    browser = get_browser()
    print("Browser initialized successfully!")
    
    # Open the site
    browser.get(site_link)
    time.sleep(5)

    # Locate the review container
    reviews_container = browser.find_element(By.CLASS_NAME, 'review-dialog-list')  # Adjust if necessary

    # Initial number of reviews
    last_review_count = len(browser.find_elements(By.CLASS_NAME, 'TSUbDb'))  # Number of review elements initially
    count = 1
    while True:
        count += 1
        print(f"{count}: Scrolling... {last_review_count}")

        # Scroll within the review container
        browser.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", reviews_container)
        time.sleep(2)  # Allow time for loading new reviews
        
        # Get the new number of review elements
        new_review_count = len(browser.find_elements(By.CLASS_NAME, 'TSUbDb'))
        
        # If the number of reviews hasn't changed, break the loop
        if new_review_count == last_review_count:
            print("No new reviews found, stopping scroll.")
            break
        
        # Otherwise, update the last_review_count and continue scrolling
        last_review_count = new_review_count
    
    location = browser.find_element(By.CLASS_NAME, 'Lhccdd').find_element(By.TAG_NAME, 'div').text
    location=clean_filename(location)
    # Continue with review scraping
    reviews = []
    review_elements = browser.find_elements(By.CLASS_NAME, 'WMbnJf')  # Locate all the reviews
    for element in review_elements:
        
        # Extract user name with retry
        user_name = try_extract(
            lambda: element.find_element(By.CLASS_NAME, 'TSUbDb').find_element(By.TAG_NAME, 'a').text,
            retries=2, default_value='Anonymous'
        )
        
        # Extract rating with retry
        rating_value = try_extract(
            lambda: float(element.find_element(By.CLASS_NAME, 'lTi8oc.z3HNkc').get_attribute("aria-label").split(" ")[1]),
            retries=2, default_value='Not Available'
        )

        # Extract review content with retry (Handle both formats)
        cleaned_review = try_extract(
            lambda: element.find_element(By.CLASS_NAME, 'review-full-text').get_attribute("innerHTML").replace('<br>', ' '),
            retries=2, 
            default_value=try_extract(
                lambda: extract_review_content(element),
                retries=2, 
                default_value='No review content available'
            )
        )

        # Extract user name with retry
        time_review_added = try_extract(
            lambda: element.find_element(By.CLASS_NAME, 'dehysf.lTi8oc').text,
            retries=2, default_value='Not Available'
        )

        reviews.append({
            'User': user_name,
            'Rating': rating_value,
            'Review': cleaned_review,
            'Date Added': time_review_added,
            'Data Collection Time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
        })
    
    # Close the browser after scraping
    browser.quit()
    return reviews,location


# Function to extract content from <span> before the <div> tag
def extract_review_content(element):
    try:
        # Get the inner HTML of the span
        review_full_text = element.find_element(By.XPATH, './/span[@data-expandable-section=""]').get_attribute("innerHTML")
        
        # Now, get everything before the first <div> tag
        index_of_div = review_full_text.find('<div')  # Find the index of the first <div> tag
        if index_of_div != -1:
            review_content = review_full_text[:index_of_div].strip()  # Take everything before the <div> tag
        else:
            review_content = review_full_text.strip()  # If no <div> found, return the entire content
        
        return review_content
    except Exception as e:
        print(f"Error extracting review content: {e}")
        return "No review content available"

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('Client connected')

def emit_progress(progress_percentage):
    socketio.emit('progress', {'percentage': progress_percentage})

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,/;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "Referer" :"http://www.google.com/"
}

def scrape_attraction_names(soup):

    attraction_names = []
    div_tags = soup.findAll('div', class_='XfVdV o AIbhI')

    return div_tags

def scrape_attraction_links(soup):

    attraction_links = []
    div_tags = soup.findAll('div', class_='alPVI eNNhq PgLKC tnGGX')

    return div_tags

def scrape_attraction_no_reviews(soup):

    div_tags = soup.find_all('section', {'data-automation': 'WebPresentation_SingleFlexCardSection'})

    return div_tags[:30]

def convert_link_to_pagination_format(link):
    pattern = r'(?<=-oa)\d+(?=-)'

    # Check if the pattern exists in the link
    match = re.search(pattern, link)

    if match:
        # If the pattern exists, replace it with {}
        new_link = re.sub(pattern, '{}', link)
    else:
        # If the pattern doesn't exist, insert -oa{}-
        new_link = re.sub(r'(?<=Activities-)', 'oa{}-', link)

    return new_link

def scrape_breadcrumb(url):
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')

    div_tag = soup.find('div', {'data-automation': 'breadcrumbs'})

    while div_tag is None:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, 'html.parser')
        div_tag = soup.find('div', {'data-automation': 'breadcrumbs'})
        time.sleep(2)

    attraction_names = [a_tag.text.strip() for a_tag in div_tag.find_all('a')]

    return '>'.join(attraction_names)

def convert_headers(headers):
    formatted_headers = {}
    for header in headers:
        key = header['key']
        value = header['value']
        formatted_headers[key] = value
    return formatted_headers

def first_scraper(headers, fetched_link, attractionCount):
  
  headers = convert_headers(headers)
  HEADERS.update(headers)
  print("")
  print(HEADERS)
  print("")
  attractionCount = int(attractionCount)
  base_url = fetched_link
  base_url = convert_link_to_pagination_format(base_url)

  url = base_url.format(0)
  bread_head= scrape_breadcrumb(url)
  print("Bread success!")
  r1 = requests.get(url, headers=HEADERS)
  soup1 = BeautifulSoup(r1.text, 'html.parser')
  time.sleep(2)
  number = 0
  div_ci = soup1.find('div', class_='Ci')
  if div_ci:
      content = div_ci.text.strip()
      last_part = content.split('of')[-1].strip()
      last_part = re.sub(r'<!--(.*?)-->', '', last_part)
      number = int(last_part.replace(',', ''))

  print(number)
  # print(number, type(number), attractionCount, type(attractionCount))
  if(attractionCount<=0):
      total_pages = math.ceil(number / 30)
  else:
      if number <= attractionCount:
        total_pages = math.ceil(number/30)
      else:
        total_pages = math.ceil(attractionCount/30)

  if not total_pages:
      total_pages=1
  print(total_pages)

  all_attraction_names = []
  section_texts = []
  ratings = []
  image_links = []
  timeStamp = []
  all_attraction_no_reviews = []
  all_attraction_links = []


  for page_number in range(total_pages):
    # HEADERS=generate_headers(user_agent_list)
    url = base_url.format(page_number * 30)
    soup = None
    while not soup:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            time.sleep(2)
        else:
            print("Failed to retrieve page. Status code:", r.status_code)
            time.sleep(2)
            continue

    attraction_names = scrape_attraction_names(soup)
    all_attraction_names.extend(attraction_names)
    attraction_no_reviews = scrape_attraction_no_reviews(soup)
    all_attraction_no_reviews.extend(attraction_no_reviews)
    attraction_links = scrape_attraction_links(soup)
    all_attraction_links.extend(attraction_links)
    print(page_number)
    # sleep_interval = random.uniform(1, 2)
    progress_percentage = (page_number + 1) / total_pages * 100
    emit_progress(progress_percentage)
    time.sleep(2)

  emit_progress(0)
  for section in all_attraction_no_reviews:
      img_tag = section.find('img')
      if img_tag:
          src_value = img_tag.get('src')
          image_links.append(src_value)
      else:
          image_links.append("")

      svg_tag = section.find('svg', class_='UctUV d H0 hzzSG')

      ########
      if svg_tag:
          title_tag = svg_tag.find('title')
          if title_tag:
              title_content = title_tag.get_text()[:3]
              ratings.append(title_content)
          else:
              ratings.append(0)
      else:
          ratings.append(0)

      ########
      span_tag = section.find('span', class_="biGQs _P pZUbB osNWb")
      if span_tag:
          section_texts.append(span_tag.get_text())
      else:
          section_texts.append('0')
      current_utc_time = datetime.now(timezone.utc)
      formatted_time = current_utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      timeStamp.append(formatted_time)

  names = [attraction.get_text() for attraction in all_attraction_names]
  names_cleaned = [name.split('. ')[1] for name in names]

  links = ["https://www.tripadvisor.com" + attraction.find('a')['href'] for attraction in all_attraction_links]

  emails = ['']*len(ratings)
  bread = [bread_head]*len(ratings)
  data = {'name': names_cleaned, 'emails':emails,'image': image_links, 'label': emails, 'phone': emails, 'rating':ratings, 'review_Count':section_texts, 'website': emails, 'breadcrumb':bread,'url':links, 'TimeStamp':timeStamp}
  df = pd.DataFrame(data)


  print(df.tail())
  print(all_attraction_names)
  print(df.shape)
  return df

def name_of_city(headers, fetched_link):
    temp_link = convert_link_to_pagination_format(fetched_link)
    parts = temp_link.split('/')
    city_part = parts[-1]
    city_parts = city_part.split('-')
    city_name = city_parts[4]
    city_name = city_name.split('_')[0]
    print(city_name)
    return {"city_name": city_name}

def add_or_param(input_link):
    index = input_link.find('Reviews')
    if index != -1:
        return input_link[:index + len('Reviews')] + '-or{}' + input_link[index + len('Reviews'):]
    else:
        return input_link

def second_scraper(headers, base_url, attractionCount):

    attractionCount = int(attractionCount)
    base_url = add_or_param(base_url)
    headers = convert_headers(headers)
    HEADERS.update(headers)
    timeStamp = []

    def scrape_attraction_name(soup):
        h1_element = soup.find('h1', class_='biGQs _P fiohW eIegw')

        # Extract the text
        if h1_element:
            name = h1_element.text
            return name
        else:
            return "Attraction"
    def extract_rating_from_div_elements(soup):
    # Initialize rating to None
      rating = None

      # Find the SVG element containing the rating
      svg_element = soup.find('svg', class_='UctUV d H0 hzzSG')
      if svg_element and svg_element.title:
          title_text = svg_element.title.get_text()
          try:
              rating_str = title_text.split(" ")[0]  # Extract the first part (rating number)
              rating = float(rating_str)
          except ValueError:
              print(f"Warning: Could not convert '{rating_str}' to float.")

      if rating is None:
          print("Rating not found.")

      return rating

    soup = None
    while not soup:
        r = requests.get(base_url, headers=HEADERS)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            time.sleep(2)
        else:
            print("Failed to retrieve page. Status code:", r.status_code)
            time.sleep(2)
            continue
    name_attraction = scrape_attraction_name(soup)
    print(name_attraction)
    rating = extract_rating_from_div_elements(soup)
    print(rating)



    def scrape_reviews(soup):
        reviews = []
        review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})

        for card in review_cards:
            review_body = card.find('span', class_='JguWG')
            if review_body:
                review_text = review_body.text.strip()
                current_utc_time = datetime.now(timezone.utc)
                formatted_time = current_utc_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                timeStamp.append(formatted_time)
                reviews.append(review_text)

        return reviews

    def scrape_review_urls(soup):
        reviews = []

        review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})

        for card in review_cards:
            div_tag = card.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX')
            if div_tag:
                a_tag = div_tag.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
                if a_tag:
                    href = a_tag.get('href')
                    reviews.append(href)
                else:
                    reviews.append('')
            else:
                reviews.append('')

        return reviews

    def scrape_profile_img(soup):
        links = []
        review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})
        for card in review_cards:
            img_tag = card.find('img')
            try:
                src = img_tag.get('src')
            except AttributeError:
                src = ""  # If no img tag found, set src to empty string
            links.append(src)
        return links

    def scrape_review_heading(soup):
        reviews = []

        review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})

        for card in review_cards:
            div_tag = card.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX')
            if div_tag:
                a_tag = div_tag.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
                if a_tag:
                    span_tag = a_tag.find('span')
                    if span_tag:
                        content = span_tag.text
                        reviews.append(content)
                    else:
                        reviews.append('')
                else:
                    reviews.append('')
            else:
                reviews.append('')
        return reviews

    def scrape_review_contributions(soup):
        reviews = []

        review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})
        for card in review_cards:
            div_tag = card.find('div', class_='biGQs _P pZUbB osNWb')
            if div_tag:
                span_tag = div_tag.find('span', class_='IugUm')
                if span_tag:
                    text_content = span_tag.text
                    match = re.search(r'\d+\s*contributions', text_content)
                    if match:
                        number_of_contributions = int(re.search(r'\d+', match.group()).group())
                        reviews.append(number_of_contributions)
                    else:
                        reviews.append(0)
                else:
                    span_tag = div_tag.find('span')
                    if span_tag:
                        text_content = span_tag.text.strip()
                        match = re.search(r'\d+\s*contributions', text_content)
                        if match:
                            number_of_contributions = int(re.search(r'\d+', match.group()).group())
                            reviews.append(number_of_contributions)
                        else:
                            reviews.append(0)
                    else:
                        reviews.append(0)
            else:
                reviews.append(0)
        return reviews

    def scrape_ratings(soup):
        ratings = []

        # Find the div with class 'LbPSX'
        div_tag = soup.find('div', class_='LbPSX')

        if div_tag:
            # Find all svg tags with the specified class within the div
            rating_tags = div_tag.find_all('svg', class_='UctUV d H0')

            for tag in rating_tags:
                title_tag = tag.find('title')
                if title_tag:
                    rating = title_tag.text.strip()
                    ratings.append(rating)

        return ratings

    def scrape_date_of_stay(soup):
        date_of_stay_list = []

        unique_div = soup.find('div', class_='LbPSX')

        if unique_div:
            tab_divs = unique_div.find_all('div', {'data-automation': 'tab'})
            if(len(tab_divs)>10):
                for div in tab_divs[:10]:
                    rpe_cd_div = div.find('div', class_='RpeCd')
                    if rpe_cd_div:
                        date_of_stay_list.append(rpe_cd_div.text.strip())
                    else:
                        date_of_stay_list.append('')
            else:
                for div in tab_divs[:len(tab_divs)-1]:
                    rpe_cd_div = div.find('div', class_='RpeCd')
                    if rpe_cd_div:
                        date_of_stay_list.append(rpe_cd_div.text.strip())
                    else:
                        date_of_stay_list.append('')
        else:
            return date_of_stay_list

        return date_of_stay_list

    def remove_or_param(url):
        # Find the index of "-or{}" in the URL
        index = url.find("-or{}")
        # If "-or{}" exists, remove it from the URL
        if index != -1:
            url = url[:index] + url[index + len("-or{}"):]
        return url
    
    def get_user_review_images(soup):
        # links = []
        # review_cards = soup.find_all('div', {'data-automation': 'reviewCard'})
        # for card in review_cards:
        #     img_tags = card.find_all('img')  # Extract all images in a review
        #     srcs = [img.get('src') for img in img_tags if img.get('src')]
        #     links.append(",".join(srcs))  # Store as comma-separated string
        # return links
        image_urls = []

        # Find all divs with class 'ajoIU'
        review_image_divs = soup.find_all('div', class_='ajoIU')

        for div in review_image_divs:
            img_tag = div.find('img')
            if img_tag and img_tag.get('src'):
                image_urls.append(img_tag['src'])  # Extract and store the src attribute
        
        return image_urls  # Return the list of all image URLs


    all_reviews = []
    review_headings = []
    date_of_stay = []
    review_urls = []
    review_contributions = []
    review_scores = []
    profile_img = []
    name_list = []
    overall_rating = []
    review_imgs = []

    r = requests.get(base_url.format(0), headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(r.text, 'html.parser')
    time.sleep(2)
    number = 0

    lbpsx_div = soup.find('div', class_='LbPSX')
    if lbpsx_div:
        tab_divs = lbpsx_div.find_all('div', {'data-automation': 'tab'})
        if tab_divs:
            last_tab_div = tab_divs[-1]
            ci_div = last_tab_div.find('div', class_='Ci')
            if ci_div:
                text_content = ci_div.get_text()
                last_number = text_content.split()[-1].replace(',', '')
                number = int(last_number)
    
    if(attractionCount<=0):
        total_pages = math.ceil(number / 10)
    else:
        if number <= attractionCount:
            total_pages = math.ceil(number/10)
        else:
            total_pages = math.ceil(attractionCount/10)
    
    if not total_pages:
        total_pages=1
    print("Number: ",number," ",total_pages)

    for page_number in range(total_pages):
        url = base_url.format(page_number * 10)
        soup = None
        while not soup:
            r = requests.get(url, headers=HEADERS)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                time.sleep(2)
            else:
                print("Failed to retrieve page. Status code:", r.status_code)
                time.sleep(2)
                continue

        reviews = scrape_reviews(soup)
        all_reviews.extend(reviews)
        reviews = scrape_review_heading(soup)
        review_headings.extend(reviews)
        reviews = scrape_date_of_stay(soup)
        date_of_stay.extend(reviews)
        reviews = scrape_review_urls(soup)
        review_urls.extend(reviews)
        reviews = scrape_review_contributions(soup)
        review_contributions.extend(reviews)
        review_score = scrape_ratings(soup)
        review_scores.extend(review_score)
        img = scrape_profile_img(soup)
        profile_img.extend(img)

        single_review_imgs = get_user_review_images(soup)
        print("Images Found: ")
        print(single_review_imgs)
        print("")
        review_imgs.extend(single_review_imgs)

        print(page_number)
        progress_percentage = (page_number + 1) / total_pages * 100
        emit_progress(progress_percentage)
        time.sleep(2)
    
    emit_progress(0)
    review_urls_final = ["https://www.tripadvisor.com"+ link for link in review_urls]

    new_url = remove_or_param(base_url)

    r = requests.get(new_url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(r.text, 'html.parser')
    time.sleep(2)
    parts = base_url.split('-')

    g_part = parts[1]
    d_part = parts[2]

    geo_id = [g_part]*len(review_scores)
    hotel_id = [d_part]*len(review_scores)

    div_tag = soup.find('div', {'data-automation': 'poi-jsonld'})
    address = [''] * len(review_scores)
    name_list = [name_attraction] * len(review_scores)
    overall_rating = [rating] * len(review_scores)
    if div_tag:
        script_tag = div_tag.find('script')

        if script_tag:
            script_text = script_tag.text.strip()

            data = json.loads(script_text)

            addressLocality = data['address'].get('addressLocality', '')  # Use get() method with a default value
            addressRegion = data['address'].get('addressRegion', '')  # Use get() method with a default value

            final_output = f"{addressLocality} {addressRegion}"
            address = [final_output] * len(review_scores)
    else:
        print("Alt")

    company_response_date = ['']*len(review_scores)
    company_response = ['']*len(review_scores)
    company_responder = ['']*len(review_scores)

    max_length = max(len(name_list), len(address), len(geo_id), len(hotel_id), len(overall_rating), len(review_urls_final), len(profile_img), len(review_scores), len(review_headings), len(review_contributions), len(all_reviews), len(date_of_stay))

    # Pad arrays with empty values if their lengths are less than the maximum length
    name_list += [''] * (max_length - len(name_list))
    address += [''] * (max_length - len(address))
    geo_id += [''] * (max_length - len(geo_id))
    hotel_id += [''] * (max_length - len(hotel_id))
    overall_rating += [''] * (max_length - len(overall_rating))
    review_urls_final += [''] * (max_length - len(review_urls_final))
    profile_img += [''] * (max_length - len(profile_img))
    review_scores += [''] * (max_length - len(review_scores))
    review_headings += [''] * (max_length - len(review_headings))
    review_contributions += [''] * (max_length - len(review_contributions))
    all_reviews += [''] * (max_length - len(all_reviews))
    date_of_stay += [''] * (max_length - len(date_of_stay))

    data = {
        'names': name_list,
        'address': address,
        'geo_id': geo_id,
        'hotel_id': hotel_id,
        'rating': overall_rating,
        'url': review_urls_final,
        'profile_image': profile_img,
        'review_score': review_scores,
        'review_heading': review_headings,
        'profile_contr': review_contributions,
        'review_body': all_reviews,
        'date_of_stay': date_of_stay,
        'company_responder': company_responder,
        'company_response': company_response,
        'company_response_date': company_response_date,
        'timestamp': timeStamp
    }

    imgs = {
        'Links': review_imgs
    }

    for key, value in data.items():
      print(f"Length of '{key}': {len(value)}")

    df = pd.DataFrame(data)
    df1 = pd.DataFrame(imgs)
    return df, df1

def second_scraper_name(headers, base_url):
    headers = convert_headers(headers)
    HEADERS.update(headers)
    r = requests.get(base_url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(r.text, 'html.parser')
    time.sleep(2)
    h1_element = soup.find('h1', class_='biGQs _P fiohW eIegw')

    Attname = "Attraction"
    # Extract the text
    if h1_element:
        name = h1_element.text
        Attname = name
    else:
        Attname = "Attraction"
    print(Attname)
    return {"city_name": Attname}

if __name__ == '__main__':
    socketio.run(app, debug=True)