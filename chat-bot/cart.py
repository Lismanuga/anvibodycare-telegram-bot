from telebot import types
from utils import get_product_info, get_products_for_category
import csv

user_carts = {}
user_selected_quantity = {}


def save_order_to_csv(user_id, email_or_phone, cart):
    file_path = "orders.csv"
    header = ["User_ID", "Email_or_Phone", "Product_Details", "Total_Price"]
    order_details = []
    total_price = 0
    for product_key, quantity in cart.items():
        category, product_index = product_key.split('_')
        product_index = int(product_index)
        products = get_products_for_category(category)
        product_name = products[product_index]
        product_info = get_product_info(product_name)
        if product_info:
            order_details.append(f"{product_info['name']} (x{quantity})")
            total_price += int(product_info['price']) * quantity
    try:
        with open(file_path, "x") as file:
            writer = csv.writer(file)
            writer.writerow(header)
    except FileExistsError:
        pass

    with open(file_path, "a") as file:
        writer = csv.writer(file)
        writer.writerow([user_id, email_or_phone, ', '.join(order_details), total_price])

    bot.send_message(user_id, "Ваше замовлення прийнято в обробку!", reply_markup=types.ReplyKeyboardRemove())
    print("Замовлення збережено в CSV файл.")



def add_to_cart(user_id, category, product_index):
    product_key = f"{category}_{product_index}"
    if user_id in user_carts:
        user_carts[user_id][product_key] = user_carts[user_id].get(product_key, 0) + 1
    else:
        user_carts[user_id] = {product_key: 1}


def remove_from_cart(user_id, category, product_index):
    product_key = f"{category}_{product_index}"
    if user_id in user_carts and product_key in user_carts[user_id]:
        del user_carts[user_id][product_key]

def clear_cart(user_id):
    if user_id in user_carts:
        del user_carts[user_id]


def generate_remove_button(product_index):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Видалити", callback_data=f"remove_{product_index}"))
    return markup


def calculate_total_price(cart):
    total_price = 0
    for product_key, quantity in cart.items():
        category, product_index = product_key.split('_')
        product_index = int(product_index)
        products = get_products_for_category(category)
        product_name = products[product_index]
        product_info = get_product_info(product_name)
        if product_info:
            total_price += int(product_info['price']) * quantity
    return total_price


def generate_cart_keyboard(cart):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="Видалити все", callback_data="clear_all"))
    markup.add(types.InlineKeyboardButton(text="Оформити замовлення", callback_data="checkout"))
    return markup


def generate_add_to_cart_button(category, product_index):
    return generate_quantity_control_keyboard(category, product_index, 1)


def set_product_quantity(user_id, product_key, quantity):
    user_selected_quantity[user_id] = user_selected_quantity.get(user_id, {})
    user_selected_quantity[user_id][product_key] = quantity


def increase_product(user_id, category, product_index):
    product_key = f"{category}_{product_index}"
    if user_id in user_carts and product_key in user_carts[user_id]:
        user_carts[user_id][product_key] += 1


def decrease_product(user_id, category, product_index):
    product_key = f"{category}_{product_index}"
    if user_id in user_carts and product_key in user_carts[user_id]:
        if user_carts[user_id][product_key] > 1:
            user_carts[user_id][product_key] -= 1
        else:
            del user_carts[user_id][product_key]


def generate_product_controls(product_key):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="+", callback_data=f"cart_increase_{product_key}"),
        types.InlineKeyboardButton(text="-", callback_data=f"cart_decrease_{product_key}"),
        types.InlineKeyboardButton(text="Видалити", callback_data=f"cart_remove_{product_key}")
    )
    return markup


def generate_quantity_control_keyboard(category, product_index, quantity, in_cart=False):
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("-", callback_data=f"decrease_{category}_{product_index}"),
        types.InlineKeyboardButton(str(quantity), callback_data="none"),
        types.InlineKeyboardButton("+", callback_data=f"increase_{category}_{product_index}")
    )
    if not in_cart:
        markup.add(types.InlineKeyboardButton("Додати до корзини", callback_data=f"add_{category}_{product_index}"))
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f"go_back_from_{category.lower()}_products"))
    return markup


user_cart_msgs = {}


def init_handlers():
    @bot.message_handler(func=lambda message: message.text == "Корзина")
    def handle_cart(message):
        msg_ids = []

        user_id = message.chat.id
        
        if user_id in user_cart_msgs:
            for msg_id in reversed(user_cart_msgs[user_id]):
                try:
                    bot.delete_message(chat_id=user_id, message_id=msg_id)
                except:
                    pass
            user_cart_msgs[user_id].clear()

        cart = user_carts.get(user_id, [])
        if not cart:
            sent_msg = bot.send_message(message.chat.id, "Ваша корзина порожня", parse_mode="Markdown", reply_markup=generate_cart_keyboard([]))
            user_cart_msgs[user_id] = msg_ids
            return
        
        sent_msg = bot.send_message(message.chat.id, "*Ваша корзина:*", parse_mode="Markdown")
        msg_ids.append(sent_msg.message_id)
        
        for product_key, quantity in cart.items():
            category, product_index = product_key.split('_')
            product_index = int(product_index)
            products = get_products_for_category(category)
            product_name = products[product_index]
            product_info = get_product_info(product_name)
            if product_info:
                product_details = f"{product_info['name']} - {product_info['price']} грн x {quantity}"
                sent_msg = bot.send_message(message.chat.id, product_details, reply_markup=generate_product_controls(product_key))
                msg_ids.append(sent_msg.message_id)
        
        total_price = calculate_total_price(cart)
        sent_msg = bot.send_message(message.chat.id, f"*Загальна вартість: {total_price} грн*\n", parse_mode="Markdown")
        msg_ids.append(sent_msg.message_id)
        sent_msg = bot.send_message(message.chat.id, "*Оберіть дію:*", parse_mode="Markdown", reply_markup=generate_cart_keyboard(cart))
        msg_ids.append(sent_msg.message_id)

        user_cart_msgs[user_id] = msg_ids


    @bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
    def handle_add_to_cart_callback(call):
        data = call.data.split('_')
        category = data[1]
        product_index = int(data[2])
        user_id = call.message.chat.id

        product_key = f"{category}_{product_index}"
        current_quantity = user_selected_quantity.get(user_id, {}).get(product_key, 1)
        
        for _ in range(current_quantity):
            add_to_cart(user_id, category, product_index)

        products = get_products_for_category(category)
        product_name = products[product_index] 
        bot.answer_callback_query(call.id, f"{current_quantity} од. {product_name} додано до вашої корзини!")


    @bot.callback_query_handler(func=lambda call: call.data.startswith("remove"))
    def handle_remove_from_cart_callback(call):
        category, product_index = call.data.replace("remove_", "").split('_')
        user_id = call.message.chat.id
        remove_from_cart(user_id, category, int(product_index))
        products = get_products_for_category(category)
        product_name = products[int(product_index)]
        bot.answer_callback_query(call.id, f"{product_name} видалено з вашої корзини!")
        handle_cart(call.message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("increase_"))
    def handle_increase_product_callback(call):
        data = call.data.split('_')
        category = data[1]
        product_index = int(data[2])
        user_id = call.message.chat.id
        increase_product(user_id, category, product_index)
        product_key = f"{category}_{product_index}"
        current_quantity = user_selected_quantity.get(user_id, {}).get(product_key, 1)
        set_product_quantity(user_id, product_key, current_quantity + 1)

        add_to_cart_markup = generate_quantity_control_keyboard(category, product_index, current_quantity + 1)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=add_to_cart_markup)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("decrease_"))
    def handle_decrease_product_callback(call):
        data = call.data.split('_')
        category = data[1]
        product_index = int(data[2])
        user_id = call.message.chat.id
        decrease_product(user_id, category, product_index)
        product_key = f"{category}_{product_index}"
        current_quantity = user_selected_quantity.get(user_id, {}).get(product_key, 1)
        if current_quantity > 1:
            set_product_quantity(user_id, product_key, current_quantity - 1)
        add_to_cart_markup = generate_quantity_control_keyboard(category, product_index, current_quantity - 1)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=add_to_cart_markup)


    @bot.callback_query_handler(func=lambda call: call.data.startswith("cart_increase_"))
    def handle_cart_increase_product_callback(call):
        product_key = call.data.replace("cart_increase_", "")
        category, product_index = product_key.split('_')
        user_id = call.message.chat.id
        increase_product(user_id, category, int(product_index))
        handle_cart(call.message)
        bot.answer_callback_query(call.id, "Кількість продукту збільшено!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cart_decrease_"))
    def handle_cart_decrease_product_callback(call):
        product_key = call.data.replace("cart_decrease_", "")
        category, product_index = product_key.split('_')
        user_id = call.message.chat.id
        decrease_product(user_id, category, int(product_index))
        handle_cart(call.message)
        bot.answer_callback_query(call.id, "Кількість продукту зменшено!")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cart_remove_"))
    def handle_cart_remove_product_callback(call):
        product_key = call.data.replace("cart_remove_", "")
        category, product_index = product_key.split('_')
        user_id = call.message.chat.id
        remove_from_cart(user_id, category, int(product_index))
        handle_cart(call.message)
        bot.answer_callback_query(call.id, f"Продукт видалено з вашої корзини!")


    @bot.callback_query_handler(func=lambda call: call.data == "checkout")
    def handle_checkout(call):
        user_id = call.message.chat.id
        msg = bot.send_message(user_id, "Будь ласка, введіть ваш імейл або номер телефону:")
        bot.register_next_step_handler(msg, process_email_or_phone)
    
    def process_email_or_phone(message):
        user_id = message.chat.id
        email_or_phone = message.text
        save_order_to_csv(user_id, email_or_phone, user_carts.get(user_id, {}))
        clear_cart(user_id)

    @bot.callback_query_handler(func=lambda call: call.data == "clear_all")
    def clear_all_from_cart_callback(call):
        user_id = call.message.chat.id
        clear_cart(user_id)
        bot.answer_callback_query(call.id, "Усі товари видалені з вашої корзини!")
        handle_cart(call.message)


def init_bot(bot_main):
    global bot
    bot = bot_main
    init_handlers()

