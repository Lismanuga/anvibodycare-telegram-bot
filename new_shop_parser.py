import requests
from bs4 import BeautifulSoup
import json


def scrape_anvibodycare(url):

    response = requests.get(url)

    if response.status_code != 200:
        print('Помилка при отриманні сторінки:', response.status_code)
        return None

    htmltext = response.text

    soup = BeautifulSoup(htmltext, 'html.parser')

    product = []

    for el in soup.find_all('div', class_='box-text box-text-products'):
        product.append(el)

    product_list = []

    for el in product:
        product_name = el.find('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link').text

        if (product_name == 'Подарункова карта'):
            continue

        product_price = el.find('span', class_='woocommerce-Price-amount amount').text.split()[0]

        product_link = el.find('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link').get('href')

        product_info = scrape_additional_product_info(product_link)

        product_data = {
            'name': product_name,
            'link': product_link,
            'price': product_price,
            'info': product_info
        }

        product_list.append(product_data)

    return product_list


def scrape_additional_product_info(url):
    response = requests.get(url)

    if response.status_code != 200:
        print('Помилка при отриманні сторінки:', response.status_code)
        return None

    htmltext = response.text

    soup = BeautifulSoup(htmltext, 'html.parser')

    info = soup.find('div', class_='product-short-description').text.strip()

    return info


product_list = scrape_anvibodycare('https://anvibodycare.com/shop/')
product_list2 = scrape_anvibodycare('https://anvibodycare.com/shop/page/2/')
merged_product_list = product_list + product_list2
product_list_json = json.dumps(merged_product_list, ensure_ascii=False)
with open('products.json', 'w', encoding='utf-8') as json_file:
    json_file.write(product_list_json)
