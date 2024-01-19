import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
import django
django.setup()

from bot.models import Car, TgUser


import requests
from bs4 import BeautifulSoup

url_source = 'https://avtoelon.uz'
# Fetch the HTML content of a web page
response = requests.get(url_source)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

div_elements = soup.find_all('div', class_='hot-item')

k = 0
for div_element in div_elements[2:3]:
    try:
        k += 1
        link = div_element.find('a')['href']
        print("URL:", link)
        single_car_url = url_source+link
        response = requests.get(single_car_url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        number = soup.find(class_='contacts-block__item')
        print(number)

        div_element = soup.find('div', class_='item product')

        span_brand = div_element.find('span', itemprop='brand')
        brand = span_brand.get_text(strip=True)

        span_name = div_element.find('span', itemprop='name')
        name = span_name.get_text(strip=True)

        span_price = div_element.find('span', class_='a-price__text')
        price = span_price.get_text(strip=True).replace(
            'y.e.', '').replace('\xa0', '').replace('~', '')

        dt_element = div_element.find('dt', class_='value-title', string='Год')
        dd_element = dt_element.find_next_sibling('dd')
        year = dd_element.get_text(strip=True)

        print(brand, name, year, price+'$')

        pairs = div_element.find_all(['dt', 'dd'])
        description = div_element.find('div', class_='description-text')
        description = description.get_text(strip=True)
        formatted_text = ''
        for i in range(0, len(pairs), 2):
            if i != 2:
                dt_text = pairs[i].get_text(strip=True)
                dd_text = pairs[i + 1].get_text(strip=True)
                formatted_text += f"{dt_text} {dd_text},\n"

        print(formatted_text+description)
        print('-'*88)

        owner = TgUser.objects.get(telegram_id=6116838287)
        car = Car.objects.create(owner=owner, name=name, model=brand, year=year, price=float(
            price), description=formatted_text+description, contact_number=single_car_url)
        print(car)
    except Exception as e:
        print(e)

print(k)
