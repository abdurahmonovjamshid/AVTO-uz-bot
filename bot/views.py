
import json
import traceback

import requests
import telebot
import telegraph
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from datetime import timedelta
from django.utils import timezone
from conf.settings import ADMINS, CHANNEL_ID, HOST, TELEGRAM_BOT_TOKEN

from .buttons.default import cencel, main_button, main_menu
from .buttons.inline import create_social_btn, urlkb
from .models import Car, Search, TgUser
from .services.addcar import (add_car, add_description, add_model, add_number,
                              add_price, add_year, paginated, search_car)
from .services.steps import USER_STEP
from rest_framework.generics import CreateAPIView
from .serializers import CarSerializer

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)


class CreateCarView(CreateAPIView):
    serializer_class = CarSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        car = self.object 
        text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\nQo'shimcha malumot: \n{car.description[:800]},\n\nBog'lanish: {car.contact_number}"
        media_group = [telebot.types.InputMediaPhoto(
            media=car.images.first().image_link, caption=text)]
        for photo in car.images.all()[1:]:
            media_group.append(
                telebot.types.InputMediaPhoto(media=photo.image_link))

        bot.send_media_group(
                    chat_id=CHANNEL_ID, media=media_group)

        return response


@csrf_exempt
def telegram_webhook(request):
    try:
        if request.method == 'POST':
            update_data = request.body.decode('utf-8')
            update_json = json.loads(update_data)
            update = telebot.types.Update.de_json(update_json)

            if update.message:
                tg_user = update.message.from_user
                telegram_id = tg_user.id
                first_name = tg_user.first_name
                last_name = tg_user.last_name
                username = tg_user.username
                is_bot = tg_user.is_bot
                language_code = tg_user.language_code

                deleted = False

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

            try:
                if update.my_chat_member.new_chat_member.status == 'kicked':
                    telegram_id = update.my_chat_member.from_user.id
                    user = TgUser.objects.get(telegram_id=telegram_id)
                    user.deleted = True
                    user.save()
            except:
                pass

            bot.process_new_updates(
                [telebot.types.Update.de_json(request.body.decode("utf-8"))])

        return HttpResponse("ok")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return HttpResponse("error")


@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def delete_car(call):
    try:
        callback_data = call.data.split(',')[0]
        messages = call.data.split(',')[1:]
        for message in messages:
            bot.delete_message(chat_id=call.from_user.id, message_id=message)

        bot.delete_message(chat_id=call.from_user.id,
                           message_id=call.message.id)

        if callback_data.startswith('del_'):
            car_id = callback_data.replace('del_', '')
            if Car.objects.filter(id=car_id).exists():
                Car.objects.filter(pk=car_id).delete()
                bot.answer_callback_query(
                    callback_query_id=call.id, text='E\'lon o\'chirildi', show_alert=True)

            else:
                bot.answer_callback_query(
                    callback_query_id=call.id, text='E\'lon avval o\'chirilgan', show_alert=True)

    except Exception as e:
        print(e)


@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        TgUser.objects.filter(telegram_id=message.from_user.id).update(
            step=USER_STEP['DEFAULT'])
        response_message = f"Salom, {message.from_user.full_name}!😊 \nBu bot sizga orzuyingizdagi 🏎 mashinani topish yoki, shaxsiy 🚘 mashinangizni tez va oson 🛒 sotuvga qo'yishingizda yordam beradi!!!"

        # Send the response message back to the user
        bot.send_photo(chat_id=message.chat.id, photo='https://telegra.ph/file/6529587f8e3bd7a9b0c56.jpg',
                       caption=response_message, reply_markup=main_button)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['all'])
def all_cars(message):
    try:
        if str(message.from_user.id) in ADMINS:
            search_car(message=message, bot=bot)
        else:
            start_handler(message)
    except Exception as e:
        print(e)


@bot.message_handler(regexp='👨‍💻 Admin')
def bot_echo(message):
    try:
        text = '''
Admin bilan bog'lanish!
(Admin sizning e'loningizni barcha AVTO-UZ foydalanuvchilariga yetkazishda yordam beradi)
'''
        bot.send_message(message.from_user.id, text=text, reply_markup=urlkb)
    except Exception as e:
        print(e)


@bot.message_handler(regexp='❌ Bekor qilish')
def cencel_car(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        if user.step == USER_STEP['SEARCH_CAR']:
            bot.send_message(chat_id=message.from_user.id, text="E\'lon qidirish bekor qilindi",
                             reply_markup=main_button, parse_mode='html')
            user.step = USER_STEP['DEFAULT']
            user.save()
        else:
            user.car_set.filter(complate=False).delete()
            user.step = USER_STEP['DEFAULT']
            user.save()
            bot.send_message(chat_id=message.from_user.id, text="E\'lon joylash bekor qilindi",
                             reply_markup=main_button, parse_mode='html')
    except Exception as e:
        print(e)


@bot.message_handler(regexp='🏠 Bosh sahifa')
def cencel_car(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        if user.step == USER_STEP['SEARCH_CAR']:
            bot.send_message(chat_id=message.from_user.id, text="E\'lon qidirish bekor qilindi",
                             reply_markup=main_button, parse_mode='html')
            user.step = USER_STEP['DEFAULT']
            user.save()
        else:
            user.car_set.filter(complate=False).delete()
            user.step = USER_STEP['DEFAULT']
            user.save()
            bot.send_message(chat_id=message.from_user.id, text="E\'lon joylash bekor qilindi",
                             reply_markup=main_button, parse_mode='html')
    except Exception as e:
        print(e)


@bot.message_handler(regexp="📝 E'lon joylash")
def cm_start(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)
        if user.car_set.all().count() < 3 or str(user.telegram_id) in ADMINS:
            TgUser.objects.filter(telegram_id=message.from_user.id).update(
                step=USER_STEP['ADD_CAR'])
            bot.send_message(
                message.from_user.id, text='📷 <b>2</b> tadan <b>6</b> tagacha Mashinangiz rasmini joylang!', reply_markup=cencel, parse_mode='html')
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text="🚫 Sizda faol e'lonlar soni ko'p")
    except Exception as e:
        print(e)


@bot.message_handler(regexp="📊 Statistika")
def statistics(message):
    try:
        if str(message.from_user.id) in ADMINS:
            threshold_date = timezone.now() - timedelta(days=15)
            # Query all cars that meet the conditions
            filtered_cars = Car.objects.filter(
                created_at__lte=threshold_date, post=True)
            for car in filtered_cars:
                car.post = False
                car.save()

            today = timezone.localdate()
            all_users = TgUser.objects.all().count()
            deleted_users = TgUser.objects.filter(deleted=True).count()
            all_cars = Car.objects.filter(post=True).count()
            bot.send_message(chat_id=message.from_user.id,
                             text=f"📊 Statistika ({today})\n\n<strong>👥 Bot foydalanuvchilari</strong>: <code>{all_users}</code>,\n       ------\n<strong>❌ O'chirilgan foydalanuvchilar</strong>: <code>{deleted_users}</code>,\n       ------\n<strong>🧾 Joylangan e'lonlar</strong>: <code>{all_cars}</code>.", parse_mode='html')
            return
        threshold_date = timezone.now() - timedelta(days=15)
        # Query all cars that meet the conditions
        filtered_cars = Car.objects.filter(
            created_at__lte=threshold_date, post=True)
        for car in filtered_cars:
            car.post = False
            car.save()

        today = timezone.localdate()
        all_users = TgUser.objects.all().count()
        all_cars = Car.objects.filter(post=True).count()
        bot.send_message(chat_id=message.from_user.id,
                         text=f"📊 Statistika ({today})\n\n<strong>👥 Bot foydalanuvchilari</strong>: <code>{all_users}</code>,\n       ------\n<strong>🧾 Joylangan e'lonlar</strong>: <code>{all_cars}</code>.", parse_mode='html')
    except Exception as e:
        print(e)


@bot.message_handler(regexp="🔍 Qidirish")
def start_search_car(message):
    try:
        TgUser.objects.filter(telegram_id=message.from_user.id).update(
            step=USER_STEP['SEARCH_CAR'])
        bot.send_message(chat_id=message.from_user.id,
                         text="Joylangan e'lonlarni qidirish uchun mashina malumotlarini kiriting", reply_markup=main_menu)

        threshold_date = timezone.now() - timedelta(days=15)
        # Query all cars that meet the conditions
        filtered_cars = Car.objects.filter(
            created_at__lte=threshold_date, post=True)
        for car in filtered_cars:
            car.post = False
            car.save()

    except Exception as e:
        print(e)


@bot.message_handler(regexp="📑 Mening e\'lonlarim")
def cm_start(message):
    try:
        user = TgUser.objects.get(telegram_id=message.from_user.id)

        threshold_date = timezone.now() - timedelta(days=15)
        # Query all cars that meet the conditions
        filtered_cars = Car.objects.filter(
            created_at__lte=threshold_date, post=True)
        for car in filtered_cars:
            car.post = False
            car.save()

        if user.car_set.exists():
            cars = user.car_set.filter(complate=True)
            for car in cars:
                try:
                    text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\nQo'shimcha malumot: \n{car.description[:800]},\n\nBog'lanish: {car.contact_number}\n\n"
                    text += f"👁: {car.seen.count()}, "
                    text += f"👍: {car.likes.count()}, "
                    text += f"👎: {car.dislikes.count()}\n\n"
                    text += f"📤 Joylandi: {car.created_at.strftime('%Y-%m-%d | %H:%M')}\n"
                    text += f"Holati: {'✅ Faol' if car.post else '❗️ Nofaol'}"
                    media_group = [telebot.types.InputMediaPhoto(
                        media=car.images.first().image_link, caption=text[:1024])]
                    for photo in car.images.all()[1:]:
                        try:
                            media_group.append(
                                telebot.types.InputMediaPhoto(media=photo.image_link))
                        except:
                            pass
                    try:
                        msg = bot.send_media_group(
                            chat_id=message.chat.id, media=media_group)
                        ids = ''
                        for a in msg:
                            ids += ','+str(a.id)
                        bot.reply_to(message=msg[0], text="Ushbu e\'lonni o\'chirish", reply_markup=InlineKeyboardMarkup().add(
                            InlineKeyboardButton(text=f'O\'chirish', callback_data=f'del_{car.id}'+ids)))
                    except Exception as e:
                        print(e)
                except:
                    return
        else:
            bot.send_message(chat_id=message.from_user.id,
                             text="Sizda e'lonlar yo'q")

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('prev') or call.data.startswith('next'))
def next_prev_calback(call):
    try:
        if call.data.startswith('prev'):
            search_id = call.data.replace('prev ', '')

            search = Search.objects.get(pk=search_id)
            text = search.text
            if search.currnet_page > 1:
                search.currnet_page -= 1
                search.save()
                page = search.currnet_page
            else:
                bot.answer_callback_query(
                    callback_query_id=call.id, text="Oldingi ro'yhat yo'q!", show_alert=True)
                return
            cars = paginated(text=text)

        if call.data.startswith('next'):
            search_id = call.data.replace('next ', '')

            search = Search.objects.get(pk=search_id)
            text = search.text

            cars = paginated(text=text)

            if len(cars) > search.currnet_page*10:
                search.currnet_page += 1
                search.save()
                page = search.currnet_page
            else:
                bot.answer_callback_query(
                    callback_query_id=call.id, text="Keyingi ro'yhat yo'q!", show_alert=True)
                return

        inline_kb = InlineKeyboardMarkup(row_width=5)
        buttons = []
        text = f"<strong>{text}</strong> so'rovi bo'yicha natijalar:\n{len(cars)} dan {page*10-9} - {page*10 if len(cars)>=page*10 else len(cars)}\n\n"
        text += "<pre>"
        text += "{:<2} {:<11} {:<6} {:<9}\n\n".format(
            "No", "Nomi", "Yili", "Narxi")
        for count, car in enumerate(cars[page*10-10: page*10]):
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

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text, parse_mode='html', reply_markup=inline_kb)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('remove '))
def remove_message(call):
    try:
        bot.delete_message(chat_id=call.from_user.id,
                           message_id=call.message.id)
        search_id = call.data.replace('remove ', '')
        if search_id:
            Search.objects.filter(pk=search_id).delete()

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('post_'))
def remove_message(call):
    try:
        if str(call.from_user.id) in ADMINS:
            callback_data = call.data.split(',')[0]

            messages = call.data.split(',')[1:]
            for message in messages:
                bot.delete_message(
                    chat_id=call.from_user.id, message_id=message)
            bot.delete_message(chat_id=call.from_user.id,
                               message_id=call.message.id)

            car_id = callback_data.replace('post_', '')
            if Car.objects.filter(pk=car_id).exists():
                car = Car.objects.get(pk=car_id)
                car.post = True
                car.save()
                bot.send_message(chat_id=car.owner.telegram_id,
                                 text=f"<b>{car}</b> e'loningiz faollashtirildi!", parse_mode='html')

                text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\nQo'shimcha malumot: \n{car.description[:800]},\n\nBog'lanish: {car.contact_number}"
                media_group = [telebot.types.InputMediaPhoto(
                    media=car.images.first().image_link, caption=text)]
                for photo in car.images.all()[1:]:
                    media_group.append(
                        telebot.types.InputMediaPhoto(media=photo.image_link))

                bot.send_media_group(
                    chat_id=CHANNEL_ID, media=media_group)

                bot.answer_callback_query(
                    callback_query_id=call.id, text="E'lon faollashtirildi!", show_alert=True)
            else:
                bot.answer_callback_query(
                    callback_query_id=call.id, text="E'lon o'chirilgan!", show_alert=True)

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('retrieve_'))
def retrieve_car(call):
    try:
        bot.answer_callback_query(callback_query_id=call.id)
        car_id = call.data.replace('retrieve_', '')
        car = Car.objects.get(pk=car_id)
        car.seen.add(TgUser.objects.get(telegram_id=call.from_user.id))

        text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\n"
        text += f"Qo'shimcha malumot: \n{car.description[:800]},\n\n"
        text += f"Bog'lanish: {car.contact_number}\n\n"
        text += f"👁: {car.seen.count()}, "
        text += f"👍: {car.likes.count()}, "
        text += f"👎: {car.dislikes.count()}\n\n"
        text += f"Joylandi: {car.created_at.strftime('%Y-%m-%d | %H:%M')}"

        if str(call.from_user.id) in ADMINS:
            text += f"\nHolati: {'✅ Faol' if car.post else '❗️ Nofaol'}"

        media_group = [telebot.types.InputMediaPhoto(
            media=car.images.first().image_link, caption=text)]
        for photo in car.images.all()[1:]:
            media_group.append(
                telebot.types.InputMediaPhoto(media=photo.image_link))

        msg = bot.send_media_group(
            chat_id=call.from_user.id, media=media_group)

        bot.reply_to(
            message=msg[0], text="E'lon xaqida fikir bildirasizmi?", reply_markup=create_social_btn(car_id))

    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('like_'))
def retrieve_car(call):
    try:
        car_id = call.data.replace('like_', '')
        car = Car.objects.get(pk=car_id)
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        car.likes.add(user)
        car.dislikes.remove(user)

        # bot.delete_message(chat_id=call.from_user.id,
        #                    message_id=call.message.id)

        reply_to_message = call.message.reply_to_message
        text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\n"
        text += f"Qo'shimcha malumot: \n{car.description[:800]},\n\n"
        text += f"Bog'lanish: {car.contact_number}\n\n"
        text += f"👁: {car.seen.count()}, "
        text += f"👍: {car.likes.count()}, "
        text += f"👎: {car.dislikes.count()}\n\n"
        text += f"Joylandi: {car.created_at.strftime('%Y-%m-%d | %H:%M')}"
        bot.edit_message_caption(
            chat_id=call.from_user.id, message_id=reply_to_message.id, caption=text)
        bot.answer_callback_query(callback_query_id=call.id)

    except Exception as e:
        bot.answer_callback_query(
            callback_query_id=call.id, text='You already liked', show_alert=True)
        print(e)


@bot.callback_query_handler(func=lambda call: call.data.startswith('dislike_'))
def retrieve_car(call):
    try:
        car_id = call.data.replace('dislike_', '')
        car = Car.objects.get(pk=car_id)
        user = TgUser.objects.get(telegram_id=call.from_user.id)
        car.dislikes.add(user)
        car.likes.remove(user)

        # bot.delete_message(chat_id=call.from_user.id,
        #                    message_id=call.message.id)

        reply_to_message = call.message.reply_to_message
        text = f"Nomi: {car.name},\nModeli: {car.model},\nIshlab chiqarilgan yil: {car.year},\nNarxi: {'{:,.2f}'.format(car.price).rstrip('0').rstrip('.')}$,\n"
        text += f"Qo'shimcha malumot: \n{car.description[:800]},\n\n"
        text += f"Bog'lanish: {car.contact_number}\n\n"
        text += f"👁: {car.seen.count()}, "
        text += f"👍: {car.likes.count()}, "
        text += f"👎: {car.dislikes.count()}\n\n"
        text += f"Joylandi: {car.created_at.strftime('%Y-%m-%d | %H:%M')}"
        bot.edit_message_caption(
            chat_id=call.from_user.id, message_id=reply_to_message.id, caption=text)
        bot.answer_callback_query(callback_query_id=call.id)

    except Exception as e:
        bot.answer_callback_query(
            callback_query_id=call.id, text='You already disliked', show_alert=True)
        print(e)


@bot.message_handler(content_types=['text', 'contact', 'photo'])
def text_handler(message):
    try:
        switcher = {
            USER_STEP['ADD_CAR']: add_car,
            USER_STEP['ADD_MODEL']: add_model,
            USER_STEP['ADD_YEAR']: add_year,
            USER_STEP['ADD_PRICE']: add_price,
            USER_STEP['ADD_DESCRIPTION']: add_description,
            USER_STEP['ADD_NUMBER']: add_number,
            USER_STEP['SEARCH_CAR']: search_car,

        }
        func = switcher.get(TgUser.objects.get(
            telegram_id=message.chat.id).step)
        if func:
            func(message, bot)
        else:
            start_handler(message)
    except Exception as e:
        # bot.send_message(313578337, f'{str(e)}')
        print(e)
        traceback.print_tb(e.__traceback__)


bot.set_webhook(url="https://"+HOST+"/webhook/")
