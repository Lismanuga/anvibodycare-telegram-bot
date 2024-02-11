import requests
from bs4 import BeautifulSoup
import json


def ab_us_anvybodycare(url):
    r = requests.get(url)
    r.text

    soup = BeautifulSoup(r.text, "html.parser")

    abus_headers_list = []
    headers_abus_dict = {'Headers': [], 'Text': []}
    list_headers = []
    list_abus = []
    all_headers = soup.find_all('h2', class_='MW5IWV')
    all_ab_us = soup.find_all('p', class_='MW5IWV')

    for ab_us in all_ab_us:
        list_abus.append(ab_us.text)

    for header in all_headers:
        list_headers.append(header.text)
    
    for header in list_headers:
        headers_abus_dict['Headers'].append(header)
    
    for ab_us in list_abus:
        headers_abus_dict['Text'].append(ab_us)
    
    abus_headers_list.append(headers_abus_dict)

    return (abus_headers_list)

def contacts_anvybodycare(url):
    r = requests.get(url)
    r.text
    contacts_data = []

    contacts_dict = {'Адреса':[],
                'Години роботи':[],
                'E-mail':[],
                'Телефон':[]}
    
    list_contacts = []

    soup = BeautifulSoup(r.text, "html.parser")
    contacts = soup.find_all('p')

    for contact in contacts:
        list_contacts.append(contact.text)
    
    for i in range(0,4,4):
        contacts_dict['Адреса'].append(list_contacts[1])
        contacts_dict['Години роботи'].append(list_contacts[2])
        contacts_dict['E-mail'].append(list_contacts[3])
        contacts_dict['Телефон'].append(list_contacts[4])

    contacts_data.append(contacts_dict)

    return contacts_data


all_data1 = ab_us_anvybodycare('https://anvibodycare.com/about-us/')
all_data2 = contacts_anvybodycare('https://anvibodycare.com/kontakty/')
merged_data =  all_data1 + all_data2
abus_contacts_list_json = json.dumps(merged_data, ensure_ascii=False)
with open('contacts_abus.json', 'w', encoding='utf-8') as json_file:
    json_file.write(abus_contacts_list_json)