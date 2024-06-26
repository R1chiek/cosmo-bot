import asyncio
from telethon import TelegramClient, errors
import logging


# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Создание файла лога
file_handler = logging.FileHandler('output.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Добавление файла лога в логгер
logging.getLogger('').addHandler(file_handler)

api_id = '23538569'  # Ваш API ID
api_hash = '1c7d17a813d63199ff41ee4b46e22a50'  # Ваш API Hash

# Чтение ссылок на исходный чат и целевые чаты из текстовых файлов
def read_chat_urls(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

source_chat_urls = read_chat_urls('source_chat.txt')
target_chat_urls = read_chat_urls('target_chats.txt')

photo_message_id = 5
alternative_message_id = 2

async def main():
    client = TelegramClient('anon', api_id, api_hash)
    
    async with client:
        try:
            source_chat = await client.get_entity(source_chat_urls[0])  # Берем первую ссылку из списка
        except errors.ChannelPrivateError:
            logging.info(f'Не удалось получить доступ к исходному чату {source_chat_urls[0]}.')
            return  # Прерываем работу скрипта, если не получается доступ к исходному чату

        while True:  # Внешний бесконечный цикл
            for target_chat_url in target_chat_urls:  # Внутренний цикл перебора чатов
                try:
                    target_chat = await client.get_entity(target_chat_url)
                    try:
                        await client.forward_messages(target_chat, photo_message_id, source_chat)
                        logging.info(f'Фото с ID {photo_message_id} успешно отправлено в {target_chat.title}.')
                    except errors.SlowModeWaitError as e:
                        logging.info(f'Необходимо подождать {e.seconds} секунд прежде чем отправить следующее сообщение в {target_chat.title}.')
                        continue  # Переход к следующему чату
                    except errors.ForbiddenError:
                        try:
                            await client.forward_messages(target_chat, alternative_message_id, source_chat)
                            logging.info(f'Альтернативное сообщение с ID {alternative_message_id} успешно отправлено в {target_chat.title}.')
                        except Exception as e:
                            logging.info(f'Ошибка при отправке альтернативного сообщения в {target_chat.title}: {e}')
                    except errors.ChannelPrivateError:
                        logging.info(f'Канал или чат {target_chat_url} является приватным или нет доступа.')
                        continue  # Переход к следующему чату
                except Exception as e:
                    logging.info(f'Ошибка при доступе к каналу или чату {target_chat_url}: {e}')
                
                

            await asyncio.sleep(1800)  # Задержка перед следующим циклом
            
logging.info(f'скрипт закончил работу')

asyncio.run(main())
