import requests
import logging
import products
import proxyhandler
from multiprocessing import Process, Lock
import time
import json
from discord_hooks import Webhook
from urllib.parse import urlparse
import re
import threading
# Get discord post formatted
# Get restock checked

urls = []
logging.basicConfig(level=logging.INFO, format = '%(asctime)s: %(message)s')
logging.basicConfig(filename='debug.log',level=logging.DEBUG, format = '%(asctime)s: %(message)s')

# get sitelist as list
sites = products.generate_sitelist('sitelist.txt')

def config():
    with open('config.json') as json_file:
        config = json.load(json_file)
        tasks = 1
        delay = config['delay']
    return tasks, delay

# executing now to prevent confusion
tasks, delay = config()
logging.info(f'SUPREME MONITOR BY @TAQUITOSLAYER - {tasks} TASKS PER SITE WITH A DELAY OF {delay} SECONDS PER PROXY BAN')

def check_if_posted(pid):
    if pid in urls:
        logging.info('PRODUCT ALREADY POSTED, IGNORING...')
    # might actually make duplicates rofl
    else:
        logging.info('NEW PRODUCT BEING ADDED TO LIST TO PREVENT DUPLICATES....')
        urls.append(pid)
        post_to_discord(pid)

def post_to_discord(product_pid):
    productz, _product_styles, _item_url, url, price = products.get_info(product_pid)
    eve_qt = 'http://remote.eve-backend.net/api/quick_task?link=' + url
    price = int(price) / 100
    parsed_uri = urlparse(url)
    result = '{uri.netloc}'.format(uri=parsed_uri)
    with open('webhook.json') as json_file:
        json_dump = json.load(json_file)
        for site_name in json_dump:
            if site_name in result:
                webhookz = json_dump[site_name]['webhook']
                print(webhookz)
                for webhook in webhookz:
                    for x in productz:
                        product = x.split('@')
                        name = product[0]
                        image = product[1]
                        stock = product[2]
                        embed = Webhook(webhook, color=13177876)
                        embed.set_desc(f'[{name}]({url})')
                        embed.add_field(name='Stock',value=stock)
                        embed.add_field(name='Price',value=price)
                        embed.add_field(name='Quick Tasks', value=f'[EVE]({eve_qt})',inline='false')
                        embed.set_thumbnail(image)
                        embed.set_footer(text=f'Supreme Monitor by @TaquitoSlayer', ts=True)
                        embed.post()

def monitor(url, proxy, task_num):
    try:
        initial_product_list = products.List(url, proxy)
    except requests.exceptions.RequestException as err:
        logging.info(f'SUPREME - {task_num} - {task_num}: ERROR: ' + err)

    while True:
        try:
            new_product_list = products.List(url, proxy)
        except requests.exceptions.RequestException as err:
            logging.info(f'SUPREME - {task_num}: ERROR: ' + err)

        diff = list(set(new_product_list) - set(initial_product_list))

        if bool(diff) == True:
            logging.info(f'SUPREME - {task_num}: NEW PRODUCT FOUND!')
            diff = set(diff)
            for product in diff:
                check_if_posted(product)
                initial_product_list = new_product_list
                time.sleep(1)

        elif bool(diff) == False:
            # logging.info(f'no new items found found - {url}')
            # logging.info(f'SUPREME - {task_num}: NO CHANGES FOUND')
            pass
        else:
            pass

def main(task_num, url, delay):
    fucked = False
    while not fucked:
        proxy_picked = proxyhandler.proxy()
        try:
            monitor(url, proxy_picked, task_num)
            fucked = True
        # simplejson.errors.JSONDecodeError
        except Exception as e:
            logging.info(f'{url.upper()} SOMETHING WRONG - {task_num} - SLEEPING FOR {delay} SECONDS')
            logging.info(f'{e}')
            time.sleep(float(delay))
            pass

def restock_monitor(url):
    # logging.info(f'SUPREME RESTOCK MONITOR - {url}')
    productz, _product_styles, _item_url, full_url, price = products.get_info(url)
    eve_qt = 'http://remote.eve-backend.net/api/quick_task?link=' + full_url
    price = int(price) / 100
    for x in productz:
        product = x.split('@')
        name = product[0]
        image = product[1]
        stock_initial = f'{name}@{int(product[2])}'
        while True:
            productz_n, _product_styles, _item_url, _url, price = products.get_info(url)
            for y in productz_n:
                product_n = y.split('@')
                stock_new = f'{name}@{int(product_n[2])}' 
                diff = list(set(stock_new) - set(stock_initial))
                if bool(diff) == True:
                    try:
                        product_n = diff[0].split('@')
                        stock = int(product_n[1])
                    except:
                        stock = 0
                    if stock > 0:
                        parsed_uri = urlparse(url)
                        result = '{uri.netloc}'.format(uri=parsed_uri)
                        with open('webhook.json') as json_file:
                            json_dump = json.load(json_file)
                            for site_name in json_dump:
                                if site_name in result:
                                    webhookz = json_dump[site_name]['webhook']
                                    print(webhookz)
                                    for webhook in webhookz:
                                        logging.info(f'NEW STOCK UPDATE FOUND')
                                        embed = Webhook(webhook, color=13177876)
                                        embed.set_desc(f'[{name}]({full_url})')
                                        embed.add_field(name='Stock',value=stock)
                                        embed.add_field(name='Price',value=price)
                                        embed.add_field(name='Quick Tasks', value=f'[EVE]({eve_qt})',inline='false')
                                        embed.set_thumbnail(image)
                                        embed.set_footer(text=f'Supreme Restock Monitor by @TaquitoSlayer', ts=True)
                                        embed.post()
                                        stock_initial = stock_new
                                elif bool(diff) == False:
                                    # logging.info(f'no changes found - {url}')
                                    pass
                                else:
                                    # logging.info('Nothing new found')
                                    pass

restock_urls = None

def update_urls():
    global restock_urls
    while True:
        proxy_picked = proxyhandler.proxy()
        site = 'https://www.supremenewyork.com/mobile_stock.json'
        try:
            restock_urls = products.List(site, proxy_picked)
            logging.info('UPDATED URLS')
            time.sleep(1800)
        except:
            pass

def update_initial():
    global restock_urls
    proxy_picked = proxyhandler.proxy()
    site = 'https://www.supremenewyork.com/mobile_stock.json'
    try:
        restock_urls = products.List(site, proxy_picked)
        logging.info('INITIAL UPDATE OF URLS')
    except:
        pass

# update restock_urls
update_initial()
updating_restock_urls = Process(target=update_urls,)
updating_restock_urls.start()
for url in restock_urls:
    logging.info('STARTING RESTOCK MONITOR FOR:' +  url)
    restock = Process(target=restock_monitor, args=(url,))
    restock.start()

for site in sites:
    for i in range(int(tasks)):
        new_items = Process(target=main, args=(i+1, site, delay,))
        new_items.start() # starting workers