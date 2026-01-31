import asyncio
import os
import random
import re
from time import sleep
from dotenv import load_dotenv
import urllib.parse

import requests
from bs4 import BeautifulSoup

'''
json argument format:
[
{
"name": "brand1",
"asin": "yes/no",
"page": "yes/no",
"image_url": "yes/no",
},
{
"name":"brand2",
"asin": "yes/no",
"image_url": "yes/no",}
]

json return format:
{
"brand1": [{"name":..., "asin":..., "page":..., "image_url":...}, {...}, ...],
"brand2": [{"name":..., "asin":..., "page":..., "image_url":...}, {...}, ...],
}
'''
load_dotenv()
MY_APIFY_TOKEN = os.getenv("MY-APIFY-TOKEN")
BRAND_URL = os.getenv("BRAND-URL")
PROXY_URL = os.getenv("PROXY-URL")


# from .models import Brand, Product
def scrape_brands(brands:dict)->dict:
    scraped_brands = []
    for brand in brands:
        fields = [key.split('scrape')[1].lower() for key,value in brand.items() if value == 'yes']
        scrape_brand = scrape_amazon_products(brand_name=brand['brandName'], fields=fields, save_db=False)
        scrape_brand['brand'] = brand['brandName']
        scraped_brands.append(scrape_brand)
        sleep(2)
    return scraped_brands


def scrape_amazon_products(brand_name, fields, save_db=True):
    main_headers = [
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3", "Accept-Language":"en-US, en:q=0.5"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36", "Accept-Language":"en-US, en:q=0.5"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Accept-Language":"en-US, en:q=0.5"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36", "Accept-Language":"en-US, en:q=0.5"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0", "Accept-Language":"en-US, en:q=0.5"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15", "Accept-Language":"en-US, en:q=0.5"}
    ]
    main_header = random.choice(main_headers)
    headers = scrape_user_agents("https://www.useragents.me/", main_header)
    # print(headers)
    proxies = get_proxies(PROXY_URL, main_header)
    if not headers:
        return None
    
    page_no = 1
    last_page_no = 1
    products = []

    # initialize brand object if save_db is True
    if save_db:
        # brand, created = Brand.objects.get_or_create(name=brand_name)
        pass

    while True:
        # stop scraping for brand when all pages have been visited
        if page_no > last_page_no:
            return products
        # Do 5 retries for brand page
        for _ in range(5):
            header = random.choice(headers)
            try:
                # 1. Get brand page
                brand_page = get_brand_page(brand_name, header, str(page_no))

                # 2. Get all products in brand page
                soup = BeautifulSoup(brand_page.content, "html.parser")
                # 3. Get href of products
                # Find all product containers (this selector may vary)
                product_tags = soup.find_all('a', {
                    'class': 'a-link-normal'
                }
                                            )

                # get last page number for brand
                if page_no == 1:
                    last_page_tag = soup.find("span", class_="s-pagination-item s-pagination-disabled")
                    if last_page_tag:
                        last_page_no = int(last_page_tag.text.strip())
                
                # stop retries since brand page successfully retrieved
                break
            except:
                sleep(2)

        # Pagination
        # increase page_no
        page_no += 1

        # 4. Go to each product page
        for product_tag in product_tags:
            for _ in range(5):
                header = random.choice(headers)
                link = product_tag.get('href')
                product_link, product_page = get_product_page(link,header)
                try:
                    parsed_product_page = BeautifulSoup(product_page.content, "html.parser")
                    # 5. Scrape product information
                    product_info = re.split('[/\\\\]', product_link)
                    name = product_info[3]
                    name = " ".join(re.split('[|,;-]',name))
                    asin = product_info[5]
                    # sku = product_page.find("span", {"class": "sku"})  # This may vary by product or may not exist
                    page = product_link

                    image_url = parsed_product_page.find("div", class_="imgTagWrapper").find("img")["src"]
                    if len(name)>5 and len(asin)<20 and image_url:
                        product = {
                            'name': name,
                            'asin': asin,
                            'page': page,
                            'image_url': image_url
                        }

                        product = {key: value for key, value in product.items() if key == 'name' or key in fields}

                        # Update product information list
                        products=save_amazon_product_container(products, product)

                        # Save product information in database
                        if save_db:
                            # save_amazon_product_db(brand, product)
                            pass

                        # move to next product by breaking for-loop
                        break
                except IndexError:
                    sleep(2)
                except AttributeError:
                    sleep(2)
            # 6. Repeat from step 4

# def save_amazon_product_db(brand, product):
#     asin = product.get('asin')

#     # Check if a product with this ASIN already exists
#     if not Product.objects.filter(asin=asin, brand=brand).exists():
#         # If it doesn't exist, create a new product entry
#         new_product=Product.objects.create(
#             name=product.get('name'),
#             asin=asin,
#             page=product.get('page'),
#             image=product.get('image_url'),
#             brand=brand
#         )
#         new_product.save()

def save_amazon_product_container(container, product):
    container.append({
                        'name': product.get('name'),
                        'asin': product.get('asin'),
                        'page': product.get('page'),
                        'image_url': product.get('image_url')
                    })
    return container


def get_brand_page(brand,header,page_no):
    brand_url = BRAND_URL + brand + "&page=" + page_no
    response = requests.get(brand_url, headers=header)
    return response


def get_product_page(product_href,header):
    # Add protocol, domain, and subdomain to only product links that don't have a full address
    if "sspa" in product_href:
        product_url = extract_https_url(product_href)
    elif "aax-us-iad" in product_href:
        product_url = "www.amazon.com" + product_href
        product_url = "https://www" + product_url.split("www")[-1]
    elif product_href.startswith("/"):
        product_url = "https://www.amazon.com" + product_href
    else:
        return None, None
    # Handle links that have prefixes e.g. links of sponsored product posts
    try:
        response = requests.get(product_url, headers=header)
        # print(response)
    except:
        return None, None
    return product_url, response


def scrape_user_agents(page_url, header):
    response = requests.get(page_url, headers=header)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        user_agents_tag = soup.find_all("textarea",{"class": "form-control ua-textarea"})
    else:
        return []
    user_agents = [{"User-Agent": user_agent.get_text(strip=True), "Accept-Language":"en-US, en:q=0.5"} for user_agent in user_agents_tag]
    return user_agents


def extract_https_url(link):
    # Parse the URL to access its query parameters
    parsed_url = urllib.parse.urlparse(link)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    # Retrieve the 'url' parameter and decode it to get the full URL
    if 'url' in query_params:
        encoded_url = query_params['url'][0]
        decoded_url = urllib.parse.unquote(encoded_url)

        # Convert the decoded relative URL to an absolute one with https
        full_url = urllib.parse.urljoin("https://www.amazon.com", decoded_url)
        return full_url
    else:
        return None  # Return None if 'url' parameter is not found


def get_proxies(api, header):
    response = requests.get(api, headers=header)
    proxies = [proxy[:-1] for proxy in response.text.strip().split("\n") if 'http' in proxy]
    return proxies



if __name__ == "__main__":
    # scrape_amazon_products("Samsung", save_db=False)
    # res=scrape_brands([{"brandName": "Swatch", "scrapeAsin": "yes", "scrapePage": "yes", "scrapeImage_url": "yes"},
    #                {"brandName": "Checkers", "scrapeAsin": "yes", "scrapePage": "no", "scrapeImage_url": "yes"}])
    # print(res)
    pass
