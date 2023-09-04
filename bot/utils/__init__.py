from io import BytesIO

import aiohttp
from loader import bot
from telebot import types


def photo_link(photo: types.PhotoSize):
    print(photo_link)
    link = photo_link
    try:
        with photo.download(BytesIO()) as file:
            form = aiohttp.FormData()
            form.add_field(
                name='file',
                value=file
            )
            with bot.session.post('https://telegra.ph/upload', data=form) as response:
                img_src = response.json()
        link = 'https://telegra.ph' + img_src[0]['src']
        return link
    except:
        pass
