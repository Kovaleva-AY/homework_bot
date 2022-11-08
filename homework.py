import logging
import os
import time
 
import requests
from telegram import Bot
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Updater

from dotenv import load_dotenv 

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth PRACTICUM_TOKEN'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    return bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(current_timestamp):
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    return response.json()



#def check_response(response):#

    #...


def parse_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('Не удалось получить название работы')
    homework_status = homework.get('status')
    if homework_status is None:
        logging.error('Не удалось получить статус работы')


    #...
    else:
        verdict = HOMEWORK_STATUSES.get(homework_status)

    #...

        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    ENV_VARS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(ENV_VARS):
        print('Отсутствует переменная')
    else:
        return True


def main():
    #"""Основная логика работы бота."""

    #...
    

    bot = Bot(token='TELEGRAM_TOKEN')
    current_timestamp = int(time.time())
    STATUS = ''
    #...

    while True:
        #try:
            response = get_api_answer(current_timestamp)

            #...
            message = parse_status((response))
            
            if message != STATUS:
                send_message(bot, message)
                STATUS = message   
            time.sleep(RETRY_TIME)
            

        #except Exception as error:
            #message = f'Сбой в работе программы: {error}'
            #...
            #time.sleep(RETRY_TIME)
        #else:
            #...

if __name__ == '__main__':
    main()



  