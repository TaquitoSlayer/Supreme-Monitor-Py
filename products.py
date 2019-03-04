import requests
import re
import json
import cfscrape
import bs4 as bs

L = requests.session()
r = cfscrape.create_scraper(sess=L)

headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0_2 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A366 Safari/600.1.4','referer': 'https://www.supremenewyork.com/mobile/'}

def generate_sitelist(textfile):
    with open(textfile) as urls:
        sitelist = urls.read().splitlines()
    return sitelist

# loop to category, then 

def List(url, proxy):
    pids = []
    new_arrivals = r.get(url, headers = headers, proxies={"http": proxy, "https": proxy})
    products_categories = new_arrivals.json()['products_and_categories']
    for category in products_categories:
        for x in products_categories[category]:
            pid = x['id']
            price = x['price']
            final = f'{pid}@{price}'
            pids.append(final)
    return pids

def get_info(pid):
    product_styles = {}
    products = []
    pid_price = pid.split('@')
    pid = pid_price[0]
    price = pid_price[1]
    url = f'https://www.supremenewyork.com/shop/{pid}'
    item_url = f'https://www.supremenewyork.com/shop/{pid}.json'
    product = r.get(item_url, headers = headers)
    styles = product.json()['styles']
    for items in styles:
        stock = items['sizes'][0]['stock_level']
        product_name = items['name']
        product_styles[product_name] = stock
        product_image = 'https:' + items['image_url']
        product_result = product_name + '@' + product_image + '@' + str(stock)
        products.append(product_result)
    return products, product_styles, item_url, url, price