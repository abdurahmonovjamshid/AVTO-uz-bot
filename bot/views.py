
import json
import traceback

import telebot
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from telebot.types import InputFile

from conf.settings import TELEGRAM_BOT_TOKEN

from .buttons.default import cencel, main_button
from .buttons.inline import urlkb
from .models import TgUser
from .services.addcar import (add_car, add_description, add_model, add_number,
                              add_price, add_year)
from .services.steps import USER_STEP

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@csrf_exempt
def telegram_webhook(request):
    try:
        if request.method == 'POST':
            update_data = request.body.decode('utf-8')
            update_json = json.loads(update_data)
            update = telebot.types.Update.de_json(update_json)

            tg_user = update.message.from_user
            telegram_id = tg_user.id
            first_name = tg_user.first_name
            last_name = tg_user.last_name
            username = tg_user.username
            is_bot = tg_user.is_bot
            language_code = tg_user.language_code

            deleted = False
            if update.message.left_chat_member and update.message.left_chat_member.id == telegram_id:
                deleted = True

            tg_user_instance, _ = TgUser.objects.update_or_create(
                telegram_id=telegram_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'is_bot': is_bot,
                    'language_code': language_code,
                    'deleted': deleted,
                }
            )
            
            bot.process_new_updates([telebot.types.Update.de_json(request.body.decode("utf-8"))])

        return HttpResponse({"status":'ok'})
    except:
        pass


@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        TgUser.objects.filter(telegram_id=message.from_user.id).update(step=USER_STEP['DEFAULT'])
        response_message = f"Salom, {message.from_user.full_name}!😊 \nBu bot sizga orzuyingizdagi 🏎 mashinani topish yoki, shaxsiy 🚘 mashinangizni tez va oson 🛒 sotuvga qo'yishingizda yordam beradi!!!"

        # Send the response message back to the user
        bot.send_photo(chat_id=message.chat.id,photo=InputFile(file='logo/logo.jpg'), caption=response_message, reply_markup=main_button)
    except Exception as e:
        print(e)


@bot.message_handler(regexp='👨‍💻 Admin')
def bot_echo(message):
    print('/'*88)
    try: 
        text = '''
Admin bilan bog'lanish!
(Admin sizning e'loningizni barcha AVTO-UZ foydalanuvchilariga yetkazishda yordam beradi)
'''
        bot.send_message(message.from_user.id, text=text, reply_markup=urlkb)
    except Exception as e:
        print(e)


@bot.message_handler(regexp='❌ Bekor qilish')
def bot_echo(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        user.car_set.filter(complate=False).delete()
        user.step = USER_STEP['DEFAULT']
        user.save()
        bot.send_message(chat_id=message.from_user.id, text="E\'lon joylash bekor qilindi", reply_markup=main_button, parse_mode='html')
    except Exception as e:
        print(e)



@bot.message_handler(regexp="📝 E'lon joylash")
def cm_start(message):
    try:
        TgUser.objects.filter(telegram_id=message.from_user.id).update(step=USER_STEP['ADD_CAR'])

        bot.send_message(message.from_user.id, text='2 tadan 6 tagacha Mashinangiz rasmini joylang!', reply_markup=cencel)
    except Exception as e:
        print(e)


@bot.message_handler(regexp="📑 Mening e\'lonlarim")
def cm_start(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        
        if user.car_set.exists():
            cars = user.car_set.filter(complate=True)
            for car in cars:

                text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {car.price},\nQo'shimcha malumot: \n{car.description},\n\nBog'lanish: {car.contact_number}"
                media_group = [telebot.types.InputMediaPhoto(media=car.images.first().image_link, caption=text)]
                for photo in car.images.all()[1:]:
                    media_group.append(telebot.types.InputMediaPhoto(media=photo.image_link))
                bot.send_media_group(chat_id=message.chat.id, media=media_group)
        else:
            bot.send_message(chat_id=message.from_user.id, text="Sizda e'lonlar yo'q")

    except Exception as e:
        print(e)





@bot.message_handler(content_types=['text', 'contact', 'photo'])
def text_handler(message):
    try:
        switcher = {
            USER_STEP['ADD_CAR'] : add_car,
            USER_STEP['ADD_MODEL'] : add_model,
            USER_STEP['ADD_YEAR'] : add_year,
            USER_STEP['ADD_PRICE'] : add_price,
            USER_STEP['ADD_DESCRIPTION'] : add_description,
            USER_STEP['ADD_NUMBER'] : add_number,

        }
        print(TgUser.objects.get(telegram_id=message.chat.id).step)
        func = switcher.get(TgUser.objects.get(telegram_id=message.chat.id).step)
        print(func)
        if func:
            func(message, bot)
        else:
            start_handler(message)
    except Exception as e:
        bot.send_message(313578337, f'{str(e)}')
        print(e)
        traceback.print_tb(e.__traceback__)