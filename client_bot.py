from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Токен вашего бота для клиентов
CLIENT_BOT_TOKEN = '7615386144:AAGEtlPLbwKmSxw2e86_I-HhqyU_-UMx-GA'

# Состояния для ConversationHandler
RESTAURANT, DELIVERY_TIME, COMMENTS, QUANTITY, PAYMENT_METHOD, ORDER_CONFIRMATION = range(6)

# Способы оплаты
PAYMENT_OPTIONS = ["Наличными", "Картой"]

# Список ресторанов (можно заменить на данные из базы данных)
RESTAURANTS = ["Ресторан 1", "Ресторан 2", "Ресторан 3"]

# Данные клиентов (в реальной системе должны быть в базе данных)
clients = {}


# Функция для регистрации нового клиента
async def start(update: Update, context):
    user_id = update.message.from_user.id
    if user_id not in clients:
        clients[user_id] = {"name": "", "phone": "", "address": "", "orders": []}

    keyboard = [
        [InlineKeyboardButton("🍽️ Сделать заказ", callback_data='make_order')],
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')],
        [InlineKeyboardButton("📝 История заказов", callback_data='order_history')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в службу доставки! Выберите действие:", reply_markup=reply_markup)


# Функция для начала оформления заказа
async def make_order(update: Update, context):
    keyboard = [
        [InlineKeyboardButton(restaurant, callback_data=restaurant) for restaurant in RESTAURANTS]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите ресторан для вашего заказа:", reply_markup=reply_markup)
    return RESTAURANT


# Функция для выбора ресторана
async def choose_restaurant(update: Update, context):
    query = update.callback_query
    restaurant = query.data
    context.user_data['restaurant'] = restaurant  # Сохраняем выбранный ресторан
    await query.answer()
    await query.edit_message_text(f"Вы выбрали {restaurant}. Теперь выберите время доставки:")

    # Кнопки для выбора времени доставки
    keyboard = [
        [InlineKeyboardButton("Сейчас", callback_data='now')],
        [InlineKeyboardButton("Через 30 минут", callback_data='30min')],
        [InlineKeyboardButton("Через 1 час", callback_data='1hour')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите время доставки:", reply_markup=reply_markup)
    return DELIVERY_TIME


# Функция для выбора времени доставки
async def choose_delivery_time(update: Update, context):
    query = update.callback_query
    delivery_time = query.data
    context.user_data['delivery_time'] = delivery_time  # Сохраняем время доставки
    await query.answer()
    await query.edit_message_text(f"Вы выбрали время доставки: {delivery_time}. Добавьте комментарий, если есть.")

    await query.message.reply_text("Введите комментарий к заказу (если нужно):")
    return COMMENTS


# Функция для ввода комментария
async def input_comments(update: Update, context):
    comment = update.message.text
    context.user_data['comment'] = comment  # Сохраняем комментарий
    await update.message.reply_text(f"Комментарий: {comment}. Теперь укажите количество каждого блюда.")

    # Запрашиваем количество
    await update.message.reply_text("Введите количество каждого блюда (например, '2 пиццы'): ")
    return QUANTITY


# Функция для ввода количества блюд
async def input_quantity(update: Update, context):
    quantity = update.message.text
    context.user_data['quantity'] = quantity  # Сохраняем количество блюд
    await update.message.reply_text(f"Количество: {quantity}. Теперь выберите способ оплаты.")

    # Кнопки для выбора способа оплаты
    keyboard = [
        [InlineKeyboardButton(method, callback_data=method) for method in PAYMENT_OPTIONS]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите способ оплаты:", reply_markup=reply_markup)
    return PAYMENT_METHOD


# Функция для выбора способа оплаты
async def choose_payment_method(update: Update, context):
    query = update.callback_query
    payment_method = query.data
    context.user_data['payment_method'] = payment_method  # Сохраняем способ оплаты
    await query.answer()

    # Отправляем финальный отчет о заказе
    order_summary = (
        f"Ваш заказ:\n"
        f"Ресторан: {context.user_data['restaurant']}\n"
        f"Время доставки: {context.user_data['delivery_time']}\n"
        f"Комментарий: {context.user_data['comment']}\n"
        f"Количество: {context.user_data['quantity']}\n"
        f"Способ оплаты: {context.user_data['payment_method']}\n\n"
        "Спасибо за заказ! Мы скоро свяжемся с вами."
    )
    await query.edit_message_text(order_summary)
    return ORDER_CONFIRMATION


# Функция для подтверждения курьером
async def confirm_delivery(update: Update, context):
    # Отправляем клиенту чек
    user_id = update.message.from_user.id
    client = clients[user_id]

    # Получаем заказ клиента
    order_summary = (
        f"Ваш заказ был доставлен и оплачен!\n\n"
        f"Ресторан: {context.user_data['restaurant']}\n"
        f"Время доставки: {context.user_data['delivery_time']}\n"
        f"Комментарий: {context.user_data['comment']}\n"
        f"Количество: {context.user_data['quantity']}\n"
        f"Способ оплаты: {context.user_data['payment_method']}\n"
        "Спасибо за заказ!"
    )

    # Отправляем чек клиенту
    await update.message.reply_text(order_summary)

    # Добавляем заказ в историю клиента
    clients[user_id]["orders"].append(order_summary)

    return ConversationHandler.END


# Основная функция для запуска
def main():
    application = Application.builder().token(CLIENT_BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CallbackQueryHandler(make_order, pattern='^make_order$')],
        states={
            RESTAURANT: [CallbackQueryHandler(choose_restaurant, pattern='^(' + '|'.join(RESTAURANTS) + ')$')],
            DELIVERY_TIME: [CallbackQueryHandler(choose_delivery_time)],
            COMMENTS: [MessageHandler(filters.TEXT, input_comments)],
            QUANTITY: [MessageHandler(filters.TEXT, input_quantity)],
            PAYMENT_METHOD: [
                CallbackQueryHandler(choose_payment_method, pattern='^(' + '|'.join(PAYMENT_OPTIONS) + ')$')],
            ORDER_CONFIRMATION: [MessageHandler(filters.TEXT, confirm_delivery)]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
