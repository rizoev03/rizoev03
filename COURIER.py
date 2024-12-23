from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Токен бота для курьеров
COURIER_BOT_TOKEN = '7917212130:AAEFauN9w-FTmhZbiSNhxgfbx-cQ-XTyi2o'

# Состояния для ConversationHandler
AVAILABLE_ORDERS, DELIVERY_CONFIRMATION, PAYMENT_CONFIRMATION = range(3)

# Данные курьеров и заказов
couriers = {}
orders = []  # Пример заказов (в реальной системе это будет база данных)


# Функция для регистрации курьера
async def start(update: Update, context):
    user_id = update.message.from_user.id
    if user_id not in couriers:
        couriers[user_id] = {"name": "", "phone": "", "assigned_order": None}

    keyboard = [
        [InlineKeyboardButton("📋 Просмотр доступных заказов", callback_data='view_orders')],
        [InlineKeyboardButton("👤 Мой профиль", callback_data='profile')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в службу доставки для курьеров! Выберите действие:",
                                    reply_markup=reply_markup)


# Функция для просмотра доступных заказов
async def view_orders(update: Update, context):
    keyboard = [
        [InlineKeyboardButton(f"Заказ #{i + 1}: {order['restaurant']}", callback_data=f'order_{i}') for i, order in
         enumerate(orders)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите заказ для выполнения:", reply_markup=reply_markup)
    return AVAILABLE_ORDERS


# Функция для принятия заказа
async def take_order(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])  # Получаем индекс заказа
    couriers[update.message.from_user.id]['assigned_order'] = orders[order_index]  # Назначаем заказ курьеру
    order = orders[order_index]

    await query.answer()
    await query.edit_message_text(
        f"Вы приняли заказ #{order_index + 1}.\n\nРесторан: {order['restaurant']}\nВремя доставки: {order['delivery_time']}\nКомментарий: {order['comment']}\n\nПодтвердите доставку:")

    keyboard = [
        [InlineKeyboardButton("✅ Доставлено", callback_data=f"delivery_confirmed_{order_index}")],
        [InlineKeyboardButton("❌ Отказаться", callback_data=f"order_{order_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Подтвердите статус доставки:", reply_markup=reply_markup)
    return DELIVERY_CONFIRMATION


# Функция для подтверждения доставки
async def confirm_delivery(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])  # Получаем индекс заказа
    order = orders[order_index]

    couriers[update.message.from_user.id]['assigned_order'] = None  # Освобождаем курьера от заказа
    await query.answer()
    await query.edit_message_text(f"Заказ #{order_index + 1} доставлен! Ожидаем подтверждения оплаты.")

    # Отправляем клиенту чек с деталями
    client = order['client']
    receipt = (
        f"Ваш заказ #{order_index + 1} был доставлен и оплачен!\n\n"
        f"Ресторан: {order['restaurant']}\n"
        f"Время доставки: {order['delivery_time']}\n"
        f"Комментарий: {order['comment']}\n"
        f"Способ оплаты: {order['payment_method']}\n"
        f"Количество: {order['quantity']}\n"
        f"Курьер: {context.message.from_user.full_name}"
    )
    await client.send_message(receipt)  # Отправляем клиенту чек
    return PAYMENT_CONFIRMATION


# Функция для подтверждения оплаты
async def confirm_payment(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])  # Получаем индекс заказа
    order = orders[order_index]

    await query.answer()
    await query.edit_message_text(f"Оплата подтверждена! Заказ #{order_index + 1} завершен.")

    return ConversationHandler.END


# Основная функция для запуска
def main():
    application = Application.builder().token(COURIER_BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AVAILABLE_ORDERS: [CallbackQueryHandler(take_order, pattern=r'^order_\d+$')],
            DELIVERY_CONFIRMATION: [CallbackQueryHandler(confirm_delivery, pattern=r'^delivery_confirmed_\d+$')],
            PAYMENT_CONFIRMATION: [CallbackQueryHandler(confirm_payment, pattern=r'^payment_confirmed_\d+$')]
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
