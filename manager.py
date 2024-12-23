import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler

# Токен бота для менеджеров
MANAGER_BOT_TOKEN = '7686309719:AAH93euKk38NwhaiBCjUmZwmb0QdrWf3CDg'

# Состояния для ConversationHandler
VIEW_ORDERS, VIEW_COURIERS, VIEW_RESTAURANTS, ADD_RESTAURANT, STATISTICS = range(5)

# Данные
orders = []  # Пример заказов
couriers = {}  # Пример курьеров
restaurants = {}  # Пример ресторанов

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция для старта
async def start(update: Update, context):
    user_id = update.message.from_user.id
    logger.info(f"User {user_id} started the bot.")
    keyboard = [
        [InlineKeyboardButton("📊 Статистика", callback_data='statistics')],
        [InlineKeyboardButton("📋 Просмотр заказов", callback_data='view_orders')],
        [InlineKeyboardButton("🚴 Курьеры", callback_data='view_couriers')],
        [InlineKeyboardButton("🍴 Рестораны", callback_data='view_restaurants')],
        [InlineKeyboardButton("➕ Добавить ресторан", callback_data='add_restaurant')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Меню для менеджера. Выберите действие:", reply_markup=reply_markup)


# Функция для обработки статистики
async def view_statistics(update: Update, context):
    logger.info("Fetching statistics.")
    total_orders = len(orders)
    total_couriers = len(couriers)
    total_restaurants = len(restaurants)

    stats = (
        f"📊 Статистика:\n"
        f"Всего заказов: {total_orders}\n"
        f"Всего курьеров: {total_couriers}\n"
        f"Всего ресторанов: {total_restaurants}\n"
    )

    await update.message.reply_text(stats)
    return STATISTICS


# Функция для обработки заказов
async def view_orders(update: Update, context):
    logger.info("Fetching orders.")
    if not orders:
        await update.message.reply_text("Нет доступных заказов.")
        return VIEW_ORDERS

    keyboard = [
        [InlineKeyboardButton(f"Заказ #{i + 1}: {order['restaurant']}", callback_data=f'order_{i}') for i, order in
         enumerate(orders)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите заказ для управления:", reply_markup=reply_markup)
    return VIEW_ORDERS


# Функция для просмотра всех курьеров
async def view_couriers(update: Update, context):
    logger.info("Fetching couriers.")
    if not couriers:
        await update.message.reply_text("Нет доступных курьеров.")
        return VIEW_COURIERS

    courier_list = "\n".join([f"{courier['name']} - {courier['status']}" for courier in couriers.values()])

    await update.message.reply_text(f"Доступные курьеры:\n{courier_list}")
    return VIEW_COURIERS


# Функция для просмотра всех ресторанов
async def view_restaurants(update: Update, context):
    logger.info("Fetching restaurants.")
    if not restaurants:
        await update.message.reply_text("Нет доступных ресторанов.")
        return VIEW_RESTAURANTS

    restaurant_list = "\n".join(
        [f"{restaurant_name}: {', '.join(details['menu'])}" for restaurant_name, details in restaurants.items()])

    await update.message.reply_text(f"Доступные рестораны:\n{restaurant_list}")
    return VIEW_RESTAURANTS


# Функция для добавления нового ресторана
async def add_restaurant(update: Update, context):
    logger.info("Adding a new restaurant.")
    await update.message.reply_text("Введите название ресторана:")
    return ADD_RESTAURANT


# Функция для добавления информации о ресторане
async def add_restaurant_info(update: Update, context):
    restaurant_name = update.message.text
    restaurants[restaurant_name] = {"menu": [], "address": "Новый адрес"}

    # Запросим меню
    await update.message.reply_text(
        f"Ресторан '{restaurant_name}' добавлен. Введите меню для ресторана (через запятую):")
    context.user_data['restaurant_name'] = restaurant_name
    return ADD_RESTAURANT


# Функция для добавления меню ресторана
async def add_menu(update: Update, context):
    restaurant_name = context.user_data['restaurant_name']
    menu = update.message.text.split(',')

    restaurants[restaurant_name]['menu'] = [item.strip() for item in menu]
    await update.message.reply_text(
        f"Меню для ресторана {restaurant_name} добавлено: {', '.join(restaurants[restaurant_name]['menu'])}")

    return VIEW_RESTAURANTS


# Функция для управления заказом
async def manage_order(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])
    order = orders[order_index]

    await query.answer()
    await query.edit_message_text(f"Информация о заказе #{order_index + 1}:\nРесторан: {order['restaurant']}\n"
                                  f"Адрес доставки: {order['address']}\nСтатус: {order['status']}")

    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить доставку", callback_data=f"confirm_delivery_{order_index}")],
        [InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_order_{order_index}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Что хотите сделать с заказом?", reply_markup=reply_markup)
    return VIEW_ORDERS


# Функция для подтверждения доставки
async def confirm_delivery(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])
    orders[order_index]['status'] = 'Доставлено'

    await query.answer()
    await query.edit_message_text(f"Заказ #{order_index + 1} был подтвержден как доставленный!")
    return VIEW_ORDERS


# Функция для отмены заказа
async def cancel_order(update: Update, context):
    query = update.callback_query
    order_index = int(query.data.split('_')[1])

    await query.answer()
    await query.edit_message_text(f"Заказ #{order_index + 1} был отменен!")
    del orders[order_index]  # Удаление заказа из списка
    return VIEW_ORDERS


# Основная функция для запуска
def main():
    application = Application.builder().token(MANAGER_BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            STATISTICS: [CallbackQueryHandler(view_statistics, pattern='^statistics$')],
            VIEW_ORDERS: [CallbackQueryHandler(view_orders, pattern='^view_orders$')],
            VIEW_COURIERS: [CallbackQueryHandler(view_couriers, pattern='^view_couriers$')],
            VIEW_RESTAURANTS: [CallbackQueryHandler(view_restaurants, pattern='^view_restaurants$')],
            ADD_RESTAURANT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_restaurant_info)],
        },
        fallbacks=[],
    )

    application.add_handler(conversation_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
