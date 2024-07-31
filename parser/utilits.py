import aiohttp
import random
import json

# from config import PROXY_TOKEN
from MWB.config import PROXY_TOKEN


headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%94%D0%B6%D0%B8%D0%BD%D1%81%D1%8B%20%D1%81%D0%B8%D0%BD%D0%B8%D0%B5',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'x-queryid': 'qid912409160171274217320240621105828',
}


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


async def wb_fetch_data(url, proxy):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, proxy=proxy, headers=headers) as response:
            if response.status == 200:
                response_data = await response.text()

                return json.loads(response_data)


async def random_proxy():
    response = await fetch_data(f"https://api.proxy6.net/{PROXY_TOKEN}/getproxy")
    print(response[1])
    if response[1] != 200:
        return response[1]
    proxy_list = []
    for item in response[0]['list'].values():
        if item["ip"] == '194.67.216.135':
            continue
        proxy_list.append({
            'server': f'{item["ip"]}:{item["port"]}',
            'username': item['user'],
            'password': item['pass']
        })

    rand_proxy = random.choice(proxy_list)
    proxy = f"http://{rand_proxy['username']}:{rand_proxy['password']}@{rand_proxy['server']}"

    proxies = {
        'http': proxy,
        'https': proxy
    }

    return proxies


async def get_categories():
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v2.json'
    rand_proxy = await random_proxy()
    response = await wb_fetch_data(url, rand_proxy['http'])

    async def recursive_values(category_list: list):
        catalog = {}
        for category in category_list:
            category_name = category['name']
            if category_name in ['Сертификаты Wildberries', 'Путешествия']:
                continue

            childs = category.get('childs')
            if childs:
                catalog[category_name] = await recursive_values(childs)
            else:
                catalog[category_name] = category['url']
        return catalog

    catalog_tree = await recursive_values(response)

    return catalog_tree
