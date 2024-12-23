import asyncio
from client_bot import main as client_main
from courier_bot import main as courier_main
from manager_bot import main as manager_main

async def start_bots():
    # Запускаем каждый бот в отдельной задаче
    await asyncio.gather(
        asyncio.to_thread(client_main),    # Запуск клиентского бота
        asyncio.to_thread(courier_main),   # Запуск курьерского бота
        asyncio.to_thread(manager_main)    # Запуск менеджерского бота
    )

if __name__ == "__main__":
    asyncio.run(start_bots())
