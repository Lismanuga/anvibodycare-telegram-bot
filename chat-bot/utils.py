import json
from telebot import types


def generate_inline_keyboard(button_dict):
    markup = types.InlineKeyboardMarkup(row_width=1)
    for label, callback_data in button_dict.items():
        button = types.InlineKeyboardButton(text=label, callback_data=callback_data)
        markup.add(button)
    return markup


def generate_keyboard(buttons_dict):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = list(buttons_dict.keys())
    for i in range(0, len(btns), 2):
        if i + 1 < len(btns):
            markup.add(btns[i], btns[i + 1])
        else:
            markup.add(btns[i])
    return markup


def get_product_info(product_name):
    try:
        with open('../products.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for product in data:
                if product['name'] == product_name:
                    return product
    except Exception as e:
        print(f"Could not load JSON: {e}")

    return None


def get_header_info():
    try:
        with open('../json_parser_abus_contacts/contacts_abus.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            headers = data[0]["Headers"]
            text = data[0]["Text"]
            header_info = "\n\n".join([f"{headers[i]}:\n{text[i]}" for i in range(len(headers))])
            return header_info
    except Exception as e:
        print(f"Could not load JSON: {e}")

    return None

def get_contact_data():
    try:
        with open('../json_parser_abus_contacts/contacts_abus.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            contact_info = data[1]
            contact_data = "\n".join([f"{key}:\n{', '.join(contact_info[key])}" for key in contact_info])
            return contact_data
    except Exception as e:
        print(f"Could not load JSON: {e}")

    return None


def get_products_for_category(category):
    body_keywords = ["дезодорант", "рук та тіла"]
    face_keywords = ["для губ і не тільки"]
    hair_keywords = ["шампунь", "твердий бальзам кондиціонер", "сироватка"]

    products = []

    try:
        with open('../products.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for row in data:
                product_name = row['name'].lower()

                if any(keyword in product_name for keyword in body_keywords) and category == "Тіло":
                    products.append(row['name'])
                elif any(keyword in product_name for keyword in face_keywords) and category == "Обличчя":
                    products.append(row['name'])
                elif any(keyword in product_name for keyword in hair_keywords) and category == "Волосся":
                    products.append(row['name'])
    except Exception as e:
        print(f"Could not load JSON: {e}")

    return products


def truncate_name(name, max_length=55):
    if len(name) > max_length:
        return name[:max_length - 3] + "..."
    return name


def truncate_callback_data(data, max_bytes=64):
    while len(data.encode('utf-8')) > max_bytes:
        data = data[:-1]
    return data


def generate_products_keyboard(category):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    if category == "Тіло":
        products = get_products_for_category("Тіло")
    elif category == "Обличчя":
        products = get_products_for_category("Обличчя")
    elif category == "Волосся":
        products = get_products_for_category("Волосся")

    for product_index, product_name in enumerate(products):
        shortened_name = truncate_name(product_name)
        callback_data = f"product_{product_index}"
        keyboard.add(types.InlineKeyboardButton(shortened_name, callback_data=callback_data))

    keyboard.add(types.InlineKeyboardButton("Назад", callback_data="go_back_to_categories"))
    return keyboard


main_buttons = {
    "Головна": "go_to_main",
    "Корзина": "........."
}
inline_buttons = {
     "Магазин": "go_to_shop",
     "Про нас": "show_about_us",
    "Контакти": "show_contacts"
}

categories = {
     "Тіло": 'show_body_products',
     "Обличчя": 'show_face_products',
     "Волосся": 'show_hair_products',
     "Назад": "go_to_main"
}

back_button = {
    "Назад": "go_back_main"
}
