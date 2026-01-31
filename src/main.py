"""Module defines the main entry point for the Apify Actor.

Feel free to modify this file to suit your specific needs.

To build Apify Actors, utilize the Apify SDK toolkit, read more at the official documentation:
https://docs.apify.com/sdk/python
"""

from __future__ import annotations
from collections import defaultdict

# Beautiful Soup - A library for pulling data out of HTML and XML files. Read more at:
# https://www.crummy.com/software/BeautifulSoup/bs4/doc
# Apify SDK - A toolkit for building Apify Actors. Read more at:
# https://docs.apify.com/sdk/python
from apify import Actor
from bs4 import BeautifulSoup

# HTTPX - A library for making asynchronous HTTP requests in Python. Read more at:
# https://www.python-httpx.org/
from httpx import AsyncClient

from .amazonScraper import scrape_brands, scrape_amazon_products


async def main() -> None:
    """Define a main entry point for the Apify Actor.

    This coroutine is executed using `asyncio.run()`, so it must remain an asynchronous function for proper execution.
    Asynchronous execution is required for communication with Apify platform, and it also enhances performance in
    the field of web scraping significantly.
    """
    async with Actor:
        # Retrieve the input object for the Actor. The structure of input is defined in input_schema.json.
        actor_input = await Actor.get_input() or {}
        brands = actor_input.get('brands')
        if not brands:
            raise ValueError('No brands set in input!')

        scraped_brands = []
        for brand in brands:
            fields = [key.split('scrape')[1].lower() for key,value in brand.items() if value == 'yes']
            scraped_brand = scrape_amazon_products(brand_name=brand['brandName'], fields=fields, save_db=False)
            scraped_brand = list(map(lambda x: {**x, 'brand': brand['brandName']}, scraped_brand))
            Actor.push_data(scraped_brand)
            scraped_brands.append(scraped_brand)

        # Build grouped object in memory
        grouped: dict[str, list[dict]] = defaultdict(list)

        for item in scraped_brands:
            brand = item.get('brand') or 'Unknown'
            grouped[brand].append(
                {
                    'name': item.get('name'),
                    'asin': item.get('asin'),
                    'page': item.get('page'),
                    'image_url': item.get('image_url'),
                }
            )

        # Store grouped JSON in the default key-value store
        #    Key: 'grouped.json'
        await Actor.set_value('grouped.json', dict(grouped))
