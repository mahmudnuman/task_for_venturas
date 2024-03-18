from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests
from csv import writer
from datetime import datetime
import validators
from time import sleep
import random
import json
import pandas as pd
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import requests
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
import logging
from selenium.common.exceptions import NoSuchElementException
from retrying import retry
import urllib3.exceptions
import requests.exceptions


page =10

start_time = datetime.now()
now = datetime.now() # current date and time
tobe_added = now.strftime("%Y-%m-%d-%H-%M-%S")
directory_path = "D:/task/"
name= directory_path + "venturas_task_" + str(tobe_added) +".xlsx"
#print(name)



@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5, retry_on_exception=lambda ex: isinstance(ex, urllib3.exceptions.HTTPError))
def get_page(url, headers):
    session = HTMLSession()
    return session.get(url, headers=headers)

@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_attempt_number=5, retry_on_exception=lambda ex: isinstance(ex, requests.exceptions.RequestException))
def get_page_requests(url, headers):
    return requests.get(url, headers=headers)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15"
]


session = HTMLSession()
content_list = []
num=0
product_count=0
for p in range(1,page+ 1):
    sleep(num)
    num = random.randint(6, 8)
    #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    user_agent = random.choice(user_agents)
    headers = {'User-Agent': user_agent}
    url = "https://shop.adidas.jp/item/?category=wear&gender=mens&page=" +str(p)
    #print('Page:',p)
    try:
        page = get_page(url, headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        lists = soup.find_all('div', class_="itemCardArea-cards test-card css-dhpxhu")
    except urllib3.exceptions.HTTPError as e:
        print(f"HTTP error fetching page {url}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error fetching page {url}: {e}")
    #print(len(lists))
    for list in lists:
        
        try:
            data = {}
            generic_name = list.find('a', href=True)

            if generic_name:
                href = generic_name.get('href')
                product_id = re.search(r'/products/(.*?)$', href).group(1) 
            else:
                product_id = ''     
            link = parent_site +'/products/'+ product_id
            
            if generic_name:
               img_tag = generic_name.find('img', class_='test-img imageSwitcherFrame test-frame')
               if img_tag:
                src_url = img_tag.get('src')
               else:
                src_url = ''
            else:
                src_url = ''
            if validators.url(link):
                sleep(7)
                user_agent = random.choice(user_agents)
                headers = {'User-Agent': user_agent}
                details_page = session.get(link,headers=headers)
                details_soup = BeautifulSoup(details_page.content,'html.parser')   

                try:
                    product_category_element = details_soup.find('span', class_="categoryName test-categoryName")
                    product_category = product_category_element.text.strip() if product_category_element else None
                except AttributeError:
                    product_category = None

                try:
                    product_name_element = details_soup.find('h1', class_="itemTitle test-itemTitle")
                    product_name = product_name_element.text.strip() if product_name_element else None
                except AttributeError:
                    if 'driver' in locals() or 'driver' in globals():
                        driver.quit()
                    product_name = None
                    break
                try:
                    product_price_element = details_soup.find('span', class_="price-value test-price-value")
                    product_price = product_price_element.text.strip() if product_price_element else None
                except AttributeError:
                    product_price = None

                data['product_id'] = product_id
                data['product_url'] = link
                data['main_image_url'] = src_url
                data['product_category'] = product_category
                data['product_name'] = product_name
                data['product_price'] = product_price

                all_sizes = details_soup.select('ul.sizeSelectorList li')
                sizes = [li.find('button').text for li in all_sizes if not li.find('button', class_='disable')]
                data['available_sizes'] = sizes

                
                sense_of_size = details_soup.find('span', class_='test-marker')
                if sense_of_size:
                    class_attribute = sense_of_size.get('class')
                    decimal_value = None
                    if class_attribute:
                        for cls in class_attribute:
                            if cls.startswith('mod-marker_'):
                                decimal_value = cls[-3:].replace('_', '.')
                                break
                else:
                    decimal_value = None

                data['sense_of_size'] = decimal_value

                
                try:
                    title_of_description_element = details_soup.find('h4', class_="heading itemFeature test-commentItem-subheading")
                    title_of_description = title_of_description_element.text.strip() if title_of_description_element else None
                except AttributeError:
                    title_of_description = None

                data['title_of_description'] = title_of_description

                try:
                    general_description_element = details_soup.find('div', class_="commentItem-mainText test-commentItem-mainText")
                    general_description = general_description_element.text.strip() if general_description_element else None
                except AttributeError:
                    general_description = None

                data['general_description'] = general_description

                itemized_general_description = details_soup.find('ul',class_="articleFeatures description_part css-1lxspbu")
                if itemized_general_description:
                    features = [li.get_text(strip=True) for li in itemized_general_description.find_all('li', class_='articleFeaturesItem')]
                    features_text = ', '.join(features)
                else:
                    features_text=''
                data['itemized_general_description'] = features_text
                
                test_categories=details_soup.find('div',class_="test-category_link null css-vxqsdw")
                if test_categories:
                    test_categories = [a.get_text(strip=True) for a in test_categories.find_all('a', class_='css-1ka7r5v')]
                    test_categories_text = ', '.join(test_categories)
                else:
                    test_categories_text=''
                data['kws'] = test_categories_text
                
            
                
            
                user_agent = random.choice(user_agents)
                headers = {'User-Agent': user_agent}
                response = requests.get(link, headers=headers)

                if response.status_code == 200:
                    
                    options = Options()
                    options.add_argument("--headless")  # Run in headless mode
                    options.add_argument("--disable-gpu")
                    logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.NOTSET)
                    driver = webdriver.Chrome(options=options)
                    #driver = webdriver.Chrome()
                    driver.get(link)
                    wait = WebDriverWait(driver, 20)

                    page_height = driver.execute_script("return document.body.scrollHeight")
                    product_count+=1
                    #print('Product Count:',product_count)
                
                    scroll_increment = 100

                    for scrolling in range(0, page_height, scroll_increment):
                        driver.execute_script(f"window.scrollTo(0, {scrolling});")
                        sleep(0.2)

                
                    sleep(5)
                
                
                    first_table = driver.find_elements(By.CSS_SELECTOR, ".sizeChartTRow th")
                    header_data = [header.text for header in first_table]

                    second_table = driver.find_elements(By.CSS_SELECTOR, ".sizeChartTRow td")
                    span_data = [span.text for span in second_table]
                    
                    second_table_rows = driver.find_elements(By.CSS_SELECTOR, ".sizeChartTRow")
                    
                    td_count=0
                    for row in second_table_rows:
                        td_count = len(row.find_elements(By.CSS_SELECTOR, "td"))
                    
            
                    
                    num_columns = td_count
                

                    sublists = [span_data[i:i+num_columns] for i in range(0, len(span_data), num_columns)]

                    size_list = {}

                    for i, sublist in enumerate(sublists):
                        size_list[header_data[i]] = sublist

                    
                    data['size_chart']=size_list

                        
                    try:
                        overall_rating_element = driver.find_element(By.CSS_SELECTOR, ".BVRRRatingNormalOutOf .BVRRNumber")
                        overall_rating = overall_rating_element.text.strip() if overall_rating_element else None
                    except NoSuchElementException:
                        overall_rating = None

                    try:
                        total_reviews_element = driver.find_element(By.CSS_SELECTOR, ".BVRRBuyAgainContainer .BVRRValue")
                        total_reviews = total_reviews_element.text.strip() if total_reviews_element else None
                        numbers = re.findall(r'\d+', total_reviews)
                        total_reviews = ''.join(numbers)
                    except NoSuchElementException:
                        total_reviews = None

                    try:
                        recommend_percentages = driver.find_element(By.CSS_SELECTOR, ".BVRRRatingPercentage .BVRRNumber")
                        total_recommend = recommend_percentages.text.strip() if recommend_percentages else None
                    except NoSuchElementException:
                        total_recommend = None

                    rating_headers = driver.find_elements(by=By.CSS_SELECTOR, value=".BVRRQuickTakeCustomWrapper .BVRRRatingHeader")
                    rating_images = driver.find_elements(by=By.CSS_SELECTOR, value=".BVRRQuickTakeCustomWrapper .BVRRRatingRadioImage img")

                    data_list = []
                    for header, image in zip(rating_headers, rating_images):
                        header_text = header.text.strip()
                        image_title = image.get_attribute("title")                   
                        data_dict = {
                            "item": header_text,
                            "rating": image_title
                        }
                        data_list.append(data_dict)

                    reviews = driver.find_elements(By.CLASS_NAME, "BVRRContentReview")
                    reviewcount=0
                    reviews_list = []
                    for review in reviews:
                        review_dict = {}  
                        reviewcount += 1
                        try:
                            rating_given_element = review.find_element(By.CLASS_NAME, "BVRRRatingNormalImage")
                            rating_given = rating_given_element.find_element(By.TAG_NAME, "img").get_attribute("title")
                        except NoSuchElementException:
                            rating_given = None

                        try:
                            review_title_by_user = review.find_element(By.CLASS_NAME, "BVRRValue").text
                        except NoSuchElementException:
                            review_title_by_user = None

                        try:
                            review_text_by_user = review.find_element(By.CLASS_NAME, "BVRRReviewText").find_element(By.TAG_NAME, "span").text
                        except NoSuchElementException:
                            review_text_by_user = None

                        try:
                            review_date_by_user = review.find_element(By.CLASS_NAME, "BVRRReviewDateContainer").find_element(By.TAG_NAME, "meta").get_attribute("content")
                        except NoSuchElementException:
                            review_date_by_user = None

                        try:
                            review_user_name = review.find_element(By.CLASS_NAME, "BVRRNickname").text
                        except NoSuchElementException:
                            review_user_name = None

                        review_dict["rating"] = rating_given
                        review_dict["review_title"] = review_title_by_user
                        review_dict["review_description"] = review_text_by_user
                        review_dict["date"] = review_date_by_user
                        review_dict["reviewer_id"] = review_user_name
                        reviews_list.append(review_dict)

                    data['rating'] = overall_rating
                    data['no_of_reviews'] = total_reviews
                    data['recommended_rate'] = total_recommend
                    data['items_review'] = data_list
                    data['reviews_list'] = reviews_list
                    content_list.append(data)
                    driver.quit()
        except Exception as e:
            print(f"Error processing product: {e}")

                #exit()
df = pd.DataFrame(content_list)
excel_file_name = f"{name}"
df.to_excel(excel_file_name, index=False)  
end_time = datetime.now()   
#print(f"Scraping completed in {(end_time - start_time).total_seconds()} seconds.")
