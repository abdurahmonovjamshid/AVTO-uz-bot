import re

import telebot
from django.db.models import Q
from django.utils import timezone
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from conf.settings import ADMINS, CHANNEL_ID

from ..buttons.default import ask_phone, main_button
from ..models import Car, CarImage, Search, TgUser
from ..services.steps import USER_STEP

phone_number_pattern = r'^\+?\d{1,3}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'


def is_phone_number(value):
    if re.match(phone_number_pattern, value):
        return True
    else:
        return False


def add_car(message, bot):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        car, created = Car.objects.get_or_create(owner=user, complate=False)
        if message.photo:
            user = TgUser.objects.get(telegram_id=message.from_user.id)

            CarImage.objects.create(
                car=car, image_link=message.photo[-1].file_id)

            if car.delete:
                bot.delete_message(
                    chat_id=message.from_user.id, message_id=car.delete)

            msg = bot.send_message(
                message.from_user.id, text='Mashina nomini kiriting', parse_mode='html')

            car.delete = msg.id
            car.save()
        elif message.text and car.images.exists():
            if 50 > len(message.text) >= 5:
                car.name = message.text.capitalize()
                car.save()
                bot.send_message(
                    message.from_user.id, text='Mashina modelini kiriting', parse_mode='html')
                user.step = USER_STEP['ADD_MODEL']
                user.save()
            else:
                bot.send_message(
                    message.from_user.id, text='Mashina nomi qabul qilinmadi.\nQayta kiriting', parse_mode='html')
        else:
            bot.send_message(
                message.from_user.id, text='Iltimos! 2 tadan 6 tagacha Mashinangiz rasmini joylang!')
    except:
        pass


def add_model(message, bot):
    model = message.text.capitalize()
    if 50 > len(model) >= 5:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        car = Car.objects.get(owner=user, complate=False)
        car.model = model
        car.save()
        user.step = USER_STEP['ADD_YEAR']
        user.save()
        bot.send_message(message.from_user.id,
                         text='Mashina ishlab chiqarilgan yilni kiriting.', parse_mode='html')
    else:
        bot.send_message(message.from_user.id,
                         text='Mashina modeli qabul qilinmadi.\nQayta kiriting.', parse_mode='html')


def add_year(message, bot):
    try:
        current_year = timezone.now().year
        print(current_year)

        if current_year >= int(message.text) >= 1999:
            year = message.text
            user = TgUser.objects.get(telegram_id=message.from_user.id)
            car = Car.objects.get(owner=user, complate=False)
            car.year = year
            car.save()
            user.step = USER_STEP['ADD_PRICE']
            user.save()
            bot.send_message(message.from_user.id,
                             text='💰 Mashina narxini kiriting! ($$$)', parse_mode='html')
        else:
            bot.send_message(
                message.from_user.id, text='Mashina ishlab chiqarilgan yilni qabul qilinmadi.\nQayta kiriting', parse_mode='html')
    except Exception as e:
        print(e)
        bot.send_message(
            message.from_user.id, text='Mashina ishlab chiqarilgan yil qabul qilinmadi.\nQayta kiriting', parse_mode='html')


def add_price(message, bot):
    try:
        price = message.text
        if float(price):
            price = float(price)
            if 9000000000.0 > price > 0.0:
                user = TgUser.objects.get(telegram_id=message.from_user.id)
                car = Car.objects.get(owner=user, complate=False)
                car.price = price
                car.save()
                user.step = USER_STEP['ADD_DESCRIPTION']
                user.save()
                bot.send_message(
                    message.from_user.id, text='📝 Mashina haqida to\'liq ma\'lumot kiriting', parse_mode='html')
    except Exception as e:
        print(e)
        bot.send_message(
            message.from_user.id, text='Mashina narxi qabul qilinmadi.\nQayta kiriting', parse_mode='html')


def add_description(message, bot):
    try:
        description = message.text
        if len(description) < 900:
            user = TgUser.objects.get(telegram_id=message.from_user.id)
            car = Car.objects.get(owner=user, complate=False)
            car.description = description
            car.save()
            user.step = USER_STEP['ADD_NUMBER']
            user.save()
            bot.send_message(message.from_user.id, text='Bog\'lanish uchun telefon raqamingizni kiriting',
                             reply_markup=ask_phone, parse_mode='html')
        else:
            bot.send_message(
                message.from_user.id, text='Mashina haqida ma\'lumot qabul qilinmadi.\nQayta kiriting', parse_mode='html')
    except:
        bot.send_message(
            message.from_user.id, text='Mashina haqida ma\'lumot qabul qilinmadi.\nQayta kiriting', parse_mode='html')


def add_number(message, bot):
    try:
        if message.content_type == 'text':
            if is_phone_number(message.text):
                contact_number = message.text
                user = TgUser.objects.get(telegram_id=message.from_user.id)
                car = Car.objects.get(owner=user, complate=False)
                car.contact_number = contact_number
                car.complate = True
                car.save()
                user.step = USER_STEP['DEFAULT']
                user.save()
                bot.send_message(message.from_user.id, text='E\'lon muvofaqiyatli joylandi',
                                 reply_markup=main_button, parse_mode='html')

            else:
                bot.send_message(
                    message.from_user.id, text='Iltimos telefon raqamini to\'g\'ri farmatda kiriting.', parse_mode='html')
        elif message.content_type == 'contact':
            contact_number = '+'+message.contact.phone_number
            user = TgUser.objects.get(telegram_id=message.from_user.id)
            car = Car.objects.get(owner=user, complate=False)
            car.contact_number = contact_number
            car.complate = True
            car.save()
            user.step = USER_STEP['DEFAULT']
            user.save()
            bot.send_message(message.from_user.id, text='E\'lon muvofaqiyatli joylandi',
                             reply_markup=main_button, parse_mode='html')

        if car:
            # send new car to admins and channel
            text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {car.price},\nQo'shimcha malumot: \n{car.description},\n\nBog'lanish: {car.contact_number}"
            media_group = [telebot.types.InputMediaPhoto(
                media=car.images.first().image_link, caption=text)]
            for photo in car.images.all()[1:]:
                media_group.append(
                    telebot.types.InputMediaPhoto(media=photo.image_link))
            for admin in ADMINS:
                msg = bot.send_media_group(
                    chat_id=admin, media=media_group)
                ids = ''
                for a in msg:
                    ids += ','+str(a.id)
                # print(ids, '\n')
                bot.reply_to(message=msg[0], text="Ushbu e\'lonni o\'chirish", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=f'O\'chirish', callback_data=f'del_{car.id}'+ids)))

            # send to channel
            bot.send_media_group(
                chat_id=CHANNEL_ID, media=media_group)

    except Exception as e:
        print(e)
        bot.send_message(
            message.from_user.id, text='Iltimos telefon raqamini to\'g\'ri farmatda kiriting.', parse_mode='html')


def get_serach_result(text, user_id):
    search_text = text
    user = TgUser.objects.get(telegram_id=user_id)

    patterns = search_text.split(' ')
    cars = []
    if search_text == '/all':
        for car in Car.objects.all():
            if car not in cars:
                cars.append(car)
    elif 50 > len(search_text) > 3:
        for pattern in patterns:
            if len(pattern) > 3:
                for car in Car.objects.filter(
                    Q(name__icontains=pattern) |
                    Q(model__icontains=pattern) |
                    Q(description__icontains=pattern) |
                    Q(price__icontains=pattern) |
                    Q(year__icontains=pattern)
                ):
                    if car not in cars:
                        cars.append(car)

    search = Search.objects.create(text=search_text, user=user)

    return {'cars': cars, 'search_id': search.id}


def paginated(text):
    search_text = text
    patterns = search_text.split(' ')
    cars = []
    if search_text == '/all':
        for car in Car.objects.all():
            if car not in cars:
                cars.append(car)
    elif 50 > len(search_text) > 3:
        for pattern in patterns:
            if len(pattern) > 3:
                for car in Car.objects.filter(
                    Q(name__icontains=pattern) |
                    Q(model__icontains=pattern) |
                    Q(description__icontains=pattern) |
                    Q(price__icontains=pattern) |
                    Q(year__icontains=pattern)
                ):
                    if car not in cars:
                        cars.append(car)

    return cars


def search_car(message, bot):
    result = get_serach_result(
        text=message.text, user_id=message.from_user.id)
    cars = result['cars']
    search_id = result['search_id']
    search_text = message.text
    print(cars)
    if 2 >= len(cars) > 0:
        for car in cars:
            text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {car.price},\nQo'shimcha malumot: \n{car.description},\n\nBog'lanish: {car.contact_number}"
            media_group = [telebot.types.InputMediaPhoto(
                media=car.images.first().image_link, caption=text)]
            for photo in car.images.all()[1:]:
                media_group.append(
                    telebot.types.InputMediaPhoto(media=photo.image_link))

            bot.send_media_group(
                chat_id=message.from_user.id, media=media_group)
    elif len(cars) > 2:
        inline_kb = InlineKeyboardMarkup(row_width=5)
        buttons = []
        text = f"<strong>{search_text}</strong> so'rovi bo'yicha natijalar:\n{len(cars)} dan 1 - {10 if len(cars)>=10 else len(cars)}\n\n"
        text += "<pre>"
        text += "{:<2} {:<11} {:<6} {:<9}\n\n".format(
            "No", "Nomi", "Yili", "Narxi")
        for count, car in enumerate(cars[:10]):
            print(car.name[:10])
            text += "{:<2} {:<11} {:<6} {:<9}$\n".format(
                str(count+1)+".", car.name[:8]+'...' if len(car.name) > 11 else car.name, car.year, car.price)
            button = InlineKeyboardButton(
                text=str(count+1), callback_data=f"retrieve_{car.id}")
            buttons.append(button)

        text += "</pre>"
        inline_kb.add(*buttons)
        inline_kb.add(InlineKeyboardButton(f'⬅', callback_data=f'prev {search_id}'),
                      InlineKeyboardButton(
                          f'❌', callback_data=f'remove {search_id}'),
                      InlineKeyboardButton(f'➡', callback_data=f'next {search_id}'))
        bot.send_message(message.from_user.id, text,
                         parse_mode='html', reply_markup=inline_kb)

    else:
        bot.send_message(message.from_user.id, text="So'rov bo'yicha xechqanday e'lon topilmadi",
                         parse_mode='html')
    print('/'*88)
