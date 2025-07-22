import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
import re
import math
from datetime import datetime, timezone
from random import randint
from IPython.display import clear_output
clear_output(wait=True)
import random

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

def convert_headers(headers):
    formatted_headers = {}
    for header in headers:
        key = header['key']
        value = header['value']
        formatted_headers[key] = value
    return formatted_headers

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
    # Find all div elements with the specified classes
      div_elements = soup.find_all('div', class_=['wSSLS', 'jVDab o W f u w GOdjs'])

      # Initialize rating to None
      rating = None

      # Iterate through div elements
      for div_element in div_elements:
          # Check if aria-label attribute is present
          if 'aria-label' in div_element.attrs:
              aria_label = div_element['aria-label']
              # Extract the rating from the aria-label attribute
              rating_str = aria_label.split(" ")[0]
              rating = float(rating_str)
              break  # Break out of the loop after finding the first rating

      if rating is None:
          print("Rating not found.")

      return rating

    soup = None
    while not soup:
        r = requests.get(base_url, headers=HEADERS)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
        else:
            print("Failed to retrieve page. Status code:", r.status_code)
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

    all_reviews = []
    review_headings = []
    date_of_stay = []
    review_urls = []
    review_contributions = []
    review_scores = []
    profile_img = []
    name_list = []
    overall_rating = []

    r = requests.get(base_url.format(0), headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
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
            else:
                print("Failed to retrieve page. Status code:", r.status_code)
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
        print(page_number)
        time.sleep(1)

    review_urls_final = ["https://www.tripadvisor.com"+ link for link in review_urls]

    new_url = remove_or_param(base_url)

    r = requests.get(new_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')

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

    for key, value in data.items():
      print(f"Length of '{key}': {len(value)}")

    df = pd.DataFrame(data)
    return df

def second_scraper_name(headers, base_url):
    headers = convert_headers(headers)
    HEADERS.update(headers)
    r = requests.get(base_url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
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