import requests
from bs4 import BeautifulSoup
import csv


def scrape_anvibodycare(url):

    response = requests.get(url)

    if response.status_code != 200:
        print('Помилка при отриманні сторінки:', response.status_code)
        return None
    
    htmltext = response.text

    soup = BeautifulSoup(htmltext, 'html.parser')

    product = []

    for el in soup.find_all('div', class_='ETPbIy nvdiI6'):
        product.append(el)
    for el in soup.find_all('div', class_='ETPbIy nvdiI6 vL5YxX'):
        product.append(el)

    product_list = []

    for el in product:
        product_name = el.find('h3', class_='s__7GeSCC oJwdGxV---typography-11-runningText oJwdGxV---priority-7-primary syHtuvM FzO_a9').text
        product_price = el.find('span', class_='cfpn1d').text
        product_image = el.find('img').get('src')
        product_link = el.find('a').get('href')
        product_list.append(product_name)
        product_list.append(product_link)
        product_list.append(product_image)
        product_list.append(product_price)

    return product_list


url = 'https://www.anvibodycare.com/shop'
product_data = scrape_anvibodycare(url)

if product_data:
    csv_filename = 'anvibodycare_products.csv'

    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Назва товару', 'Посилання на товар', 'Посилання на картинку', 'Ціна']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        
        for i in range(0, len(product_data), 4):
            product_dict = {
                'Назва товару': product_data[i],
                'Посилання на товар': product_data[i + 1],
                'Посилання на картинку': product_data[i + 2],
                'Ціна': product_data[i + 3]
            }
            writer.writerow(product_dict)

    print(f'Дані збережено в файлі {csv_filename}.')
else:
    print('Дані не були знайдені.')
