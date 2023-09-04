from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

urlkb = InlineKeyboardMarkup(row_width=1)
urlbutton = InlineKeyboardButton(text='👨‍💻 Admin', url='https://t.me/Jamshid_Abdurahmonov1')
urlkb.add(urlbutton)