import re

from ..buttons.default import ask_phone, main_button
from ..models import Car, CarImage, TgUser
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
            CarImage.objects.create(car=car, image_link=message.photo[-1].file_id)

            if not created:
                bot.delete_message(chat_id=message.from_user.id, message_id=car.delete)


            msg = bot.send_message(message.from_user.id, text='Mashina nomini kiriting', parse_mode='html')

            car.delete = msg.id
            car.save()
        elif message.text and car.images.exists():
            if len(message.text)>=5:
                car.name = message.text.capitalize()
                car.save()
                bot.send_message(message.from_user.id, text='Mashina modelini kiriting', parse_mode='html')
                user.step = USER_STEP['ADD_MODEL']
                user.save()
            else:
                bot.send_message(message.from_user.id, text='Mashina nomi qabul qilinmadi.\nQayta kiriting', parse_mode='html')
        else:
            bot.send_message(message.from_user.id, text='Iltimos! 2 tadan 6 tagacha Mashinangiz rasmini joylang!')
    except:
        pass    


def add_model(message, bot):
    model = message.text.capitalize()
    user = TgUser.objects.get(telegram_id=message.from_user.id)
    car = Car.objects.get(owner=user, complate=False)
    car.model = model
    car.save()
    user.step = USER_STEP['ADD_YEAR']
    user.save()
    bot.send_message(message.from_user.id, text='Mashina ishlab chiqarilgan yilni kiriting', parse_mode='html')


def add_year(message, bot):
    try:
        if 2024 >= int(message.text) >= 1999:
            year = message.text
            user = TgUser.objects.get(telegram_id=message.from_user.id)
            car = Car.objects.get(owner=user, complate=False)
            car.year = year
            car.save()
            user.step = USER_STEP['ADD_PRICE']
            user.save()
            bot.send_message(message.from_user.id, text='Mashina narxini kiriting', parse_mode='html')
        else:
            bot.send_message(message.from_user.id, text='Mashina ishlab chiqarilgan yilni qabul qilinmadi.\nQayta kiriting', parse_mode='html')
    except:
        bot.send_message(message.from_user.id, text='Mashina ishlab chiqarilgan yil qabul qilinmadi.\nQayta kiriting', parse_mode='html')



def add_price(message, bot):
    try:
        price = message.text
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        car = Car.objects.get(owner=user, complate=False)
        car.price = price
        car.save()
        user.step = USER_STEP['ADD_DESCRIPTION']
        user.save()
        bot.send_message(message.from_user.id, text='Mashina haqida to\'liq ma\'lumot kiriting', parse_mode='html')
    except:
        bot.send_message(message.from_user.id, text='Mashina narxi qabul qilinmadi.\nQayta kiriting', parse_mode='html')



def add_description(message, bot):
    try:
        description = message.text
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        car = Car.objects.get(owner=user, complate=False)
        car.description = description
        car.save()
        user.step = USER_STEP['ADD_NUMBER']
        user.save()
        bot.send_message(message.from_user.id, text='Bog\'lanish uchun telefon raqamingizni kiriting',reply_markup=ask_phone, parse_mode='html')
    except:
        bot.send_message(message.from_user.id, text='Mashina haqida ma\'lumot qabul qilinmadi.\nQayta kiriting', parse_mode='html')



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
                bot.send_message(message.from_user.id, text='E\'lon muvofaqiyatli joylandi',reply_markup=main_button, parse_mode='html')
            else:
                bot.send_message(message.from_user.id, text='Iltimos telefon raqamini to\'g\'ri farmatda kiriting.', parse_mode='html')
        elif message.content_type == 'contact':
            contact_number = message.contact.phone_number
            user = TgUser.objects.get(telegram_id=message.from_user.id)
            car = Car.objects.get(owner=user, complate=False)
            car.contact_number = contact_number
            car.complate = True
            car.save()
            user.step = USER_STEP['DEFAULT']
            user.save()
            bot.send_message(message.from_user.id, text='E\'lon muvofaqiyatli joylandi',reply_markup=main_button, parse_mode='html')
    except Exception as e:
        print(e)
        bot.send_message(message.from_user.id, text='Iltimos telefon raqamini to\'g\'ri farmatda kiriting.', parse_mode='html')
