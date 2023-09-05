from telebot.types import KeyboardButton, ReplyKeyboardMarkup

main_button = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

main_button.add('🔍 Qidirish', "📝 E'lon joylash")
main_button.add('📑 Mening e\'lonlarim',)
main_button.add('📊 Statistika', '👨‍💻 Admin')


cencel = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('❌ Bekor qilish'))


ask_phone = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton(
    '☎️ Raqam jo\'natish', request_contact=True), KeyboardButton('❌ Bekor qilish'))
