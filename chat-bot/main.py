import telebot
from telebot import types
import config
from utils import generate_keyboard, generate_inline_keyboard, generate_products_keyboard, get_product_info, get_products_for_category, get_contact_data, get_header_info, back_button, main_buttons, inline_buttons, categories 
import cart
from cart import save_order_to_csv


TOKEN = config.TOKEN
bot = telebot.TeleBot(TOKEN)
text = 'ANVI bodycare крафтове виробництво разом обираємо свідоме споживання та виготовляємо природні продукти з натуральних олій глин та рослин'


user_navigation_history = {}

@bot.message_handler(func=lambda message: message.text == "Головна")
def main_button(message):
    bot.send_message(message.chat.id, text, reply_markup=generate_inline_keyboard(inline_buttons))



@bot.message_handler(commands=['start'])
def handle_start(message):
    welcome_text = (
        f'Привіт {message.from_user.first_name}! '
        'Ми вітаємо вас у нашому Telegram боті, який створений для зручного '
        'перегляду та покупки наших товарів, а також для отримання інформації '
        'про нашу компанію та філософію. '
        'Для більш детальної інформації та покупок відвідайте наш веб-магазин: '
        '[ANVI Body Care](https://www.anvibodycare.com)'
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=welcome_text,
        reply_markup=generate_keyboard(main_buttons),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )


@bot.callback_query_handler(func=lambda call: call.data == 'go_to_shop')
def handle_shop_button(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="*Оберіть категорію: *\n",
        parse_mode="Markdown",
        reply_markup=generate_inline_keyboard(categories)
    )


@bot.callback_query_handler(func=lambda call: call.data == 'go_back_main')
def handle_back_button(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="*Ви знову в головному меню: *\n",
        parse_mode="Markdown",
        reply_markup=generate_inline_keyboard(inline_buttons)
    )

@bot.message_handler(commands=['show_about_us'])
def handle_about_us(message):
    about_us_info = get_header_info()
    if about_us_info:
        bot.send_message(message.chat.id, about_us_info)
    else:
        bot.send_message(message.chat.id, "Вибачте, інформація відсутня.")



@bot.message_handler(commands=['show_contacts'])
def handle_show_contacts(message):
    contact_info = get_contact_data()
    if contact_info:
        bot.send_message(message.chat.id, contact_info)
    else:
        bot.send_message(message.chat.id, "Вибачте, інформація відсутня.")



@bot.callback_query_handler(func=lambda call: call.data == 'show_body_products')
def show_body_products(call):
    add_to_navigation_history(call.message.chat.id, "Тіло")
    bot.send_message(
        chat_id=call.message.chat.id,
        text="\n*Оберіть продукт для категорії Тіло:*",
        parse_mode="Markdown",
        reply_markup=generate_products_keyboard("Тіло")
    )


@bot.callback_query_handler(func=lambda call: call.data == 'show_face_products')
def show_face_products(call):
    add_to_navigation_history(call.message.chat.id, "Обличчя")
    bot.send_message(
        chat_id=call.message.chat.id,
        text="\n*Оберіть продукт для категорії Обличчя:*",
        parse_mode="Markdown",
        reply_markup=generate_products_keyboard("Обличчя")
    )

@bot.callback_query_handler(func=lambda call: call.data == 'show_hair_products')
def show_hair_products(call):
    add_to_navigation_history(call.message.chat.id, "Волосся")
    bot.send_message(
        chat_id=call.message.chat.id,
        text="\n*Оберіть продукт для категорії Волосся:*",
        parse_mode="Markdown",
        reply_markup=generate_products_keyboard("Волосся")
    )


@bot.callback_query_handler(func=lambda call: call.data == 'go_to_main')
def go_to_main(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="*Головне меню:*",
        parse_mode="Markdown",
        reply_markup=generate_inline_keyboard(inline_buttons)
    )


@bot.callback_query_handler(func=lambda call: call.data == 'show_about_us')
def handle_about_us_callback(call):
    about_us_info = get_header_info() 
    if about_us_info:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=about_us_info,
            reply_markup=generate_inline_keyboard(back_button)
        )
    else:
        bot.send_message(call.message.chat.id, "Вибачте, інформація відсутня.")

@bot.callback_query_handler(func=lambda call: call.data == 'show_contacts')
def handle_show_contacts_callback(call):
    contact_info = get_contact_data()
    if contact_info:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=contact_info,
            reply_markup=generate_inline_keyboard(back_button)
        )
    else:
        bot.send_message(call.message.chat.id, "Вибачте, інформація відсутня.")


@bot.callback_query_handler(func=lambda call: call.data == 'go_back_to_categories')
def handle_back_to_categories(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="\n*Оберіть категорію:*",
        parse_mode="Markdown",
        reply_markup=generate_inline_keyboard(categories)
    )

def add_to_navigation_history(user_id, category):
    if user_id not in user_navigation_history:
        user_navigation_history[user_id] = []
    user_navigation_history[user_id].append(category)


@bot.callback_query_handler(func=lambda call: call.data.startswith("go_back_from_"))
def handle_go_back_from_category(call):
    user_id = call.message.chat.id
    if user_id not in user_navigation_history or not user_navigation_history[user_id]:
        bot.answer_callback_query(call.id, "Історія навігації відсутня.")
        return

    last_category = user_navigation_history[user_id].pop()
    
    if last_category == "Тіло":
        show_body_products(call)
    elif last_category == "Обличчя":
        show_face_products(call)
    elif last_category == "Волосся":
        show_hair_products(call)
    else:
        handle_shop_button(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
def handle_product_button(call):
    product_index = int(call.data.split('_')[1])
    if "Тіло" in call.message.text:
        category = "Тіло"
    elif "Обличчя" in call.message.text:
        category = "Обличчя"
    elif "Волосся" in call.message.text:
        category = "Волосся"
    else:
        bot.answer_callback_query(call.id, "Не вдалося визначити категорію продукту. Спробуйте ще раз.")
        return

    products = get_products_for_category(category)
    product_name = products[product_index]
    product_info = get_product_info(product_name)
    if not product_info:
        bot.answer_callback_query(call.id, "Не вдалося отримати інформацію про продукт. Спробуйте ще раз.")
        return
    
    product_details = f"{product_info['name']} - {product_info['price']} грн\n[Детальніше]({product_info['link']})"
    add_to_cart_markup = cart.generate_quantity_control_keyboard(category, product_index, 1)
    bot.send_message(call.message.chat.id, product_details, parse_mode='Markdown', reply_markup=add_to_cart_markup)


def main():
    cart.init_bot(bot)
    bot.polling(none_stop=True)


if __name__ == '__main__':
    main()
