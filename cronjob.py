from bs4 import BeautifulSoup
import requests
import django
import os
import sys
import telebot
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings")
django.setup()
from bot.models import Car, TgUser, CarImage
from bot.views import bot




url_source = 'https://avtoelon.uz'
# Fetch the HTML content of a web page
response = requests.get(url_source)
html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

div_elements = soup.find_all('div', class_='hot-item')

k = 0
for div_element in div_elements[1:]:
    try:
        k += 1
        link = div_element.find('a')['href']
        # print("URL:", link)
        single_car_url = url_source+link
        time.sleep(2)
        response = requests.get(single_car_url)
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        number = soup.find(class_='contacts-block__item')
        # print(number)

        div_element = soup.find('div', class_='item product')

        span_brand = div_element.find('span', itemprop='brand')
        brand = span_brand.get_text(strip=True)

        span_name = div_element.find('span', itemprop='name')
        name = span_name.get_text(strip=True).replace(',', '')

        span_price = div_element.find('span', class_='a-price__text')
        price = span_price.get_text(strip=True).replace(
            'y.e.', '').replace('\xa0', '').replace('~', '')

        dt_element = div_element.find('dt', class_='value-title', string='Год')
        dd_element = dt_element.find_next_sibling('dd')
        year = dd_element.get_text(strip=True)

        # print(brand, name, year, price+'$')

        pairs = div_element.find_all(['dt', 'dd'])
        description = div_element.find('div', class_='description-text').get_text(separator=' ').strip()
        formatted_text = ''
        for i in range(0, len(pairs), 2):
            if i != 2:
                dt_text = pairs[i].get_text(strip=True)
                dd_text = pairs[i + 1].get_text(strip=True)
                formatted_text += f"{dt_text} {dd_text},\n"

        # print(formatted_text+description)
        # print('-'*88)
        if not Car.objects.filter(contact_number=single_car_url).exists():
            owner = TgUser.objects.get(telegram_id=6116838287)
            car = Car.objects.create(owner=owner, name=name, model=brand, year=year, price=float(
                price), description=formatted_text+description, contact_number=single_car_url, complate=True, post=True)

            photo_tags = div_element.find_all('a', class_='small-thumb')
            main_photo = div_element.find('div', class_='main-photo')
            try:
                CarImage.objects.create(
                    car=car, image_link=main_photo.a.get('href'), telegraph=main_photo.a.get('href'))
                for i, photo_tag in enumerate(photo_tags[1:]):
                    if i >= 6:  # Maximum number of photos reached
                        break
                    href = photo_tag.get('href')

                    CarImage.objects.create(car=car, image_link=href, telegraph=href)
                print(car)
                
                # try:
                #     text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\nQo'shimcha malumot: \n{car.description},\n\nBog'lanish: {car.contact_number}"
                #     media_group = [telebot.types.InputMediaPhoto(
                #         media=car.images.first().image_link, caption=text)]
                #     for photo in car.images.all()[1:]:
                #         media_group.append(
                #             telebot.types.InputMediaPhoto(media=photo.image_link))

                #     bot.send_media_group(
                #         chat_id=-1001922246677, media=media_group)
                # except Exception as e:
                #     print(e)
            except:
                car.delete()
                print('deleted')
        else:
            print('car found')

    except Exception as e:
        print(e)

print(k)
