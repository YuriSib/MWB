import aiohttp
import random
import json

from config import PROXY_TOKEN


headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Origin': 'https://www.wildberries.ru',
    'Referer': 'https://www.wildberries.ru/catalog/0/search.aspx?search=%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80%20%D0%B1%D0%B5%D0%BD%D0%B7%D0%B8%D0%BD%D0%BE%D0%B2%D1%8B%D0%B9',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 YaBrowser/23.11.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="118", "YaBrowser";v="23.11", "Not=A?Brand";v="99", "Yowser";v="2.5"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'x-queryid': 'qid166042518169737901020240607174105',
}


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(), response.status


async def wb_fetch_data(url, proxy):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, proxy=proxy) as response:
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
