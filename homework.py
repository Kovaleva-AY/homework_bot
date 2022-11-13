import logging
import os
import time
from http import HTTPStatus
import requests
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


class Error(Exception):
    """Базовый класс исключений."""
    pass


class NoKeyInAPIResponseError(Error):
    """Отсутствует ключ "status" в ответе API."""
    pass


class UnknownHomeWorkStatusError(Error):
    """Неизвестный статус домашней работы."""
    pass


class HomeWorkKeyError(Error):
    """Отсутствует ключ "homework_name" в ответе API."""
    pass


def send_message(bot, message):
    """Отправляет сообщение в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.info('Сообщение отправлено')
    except Exception:
        logging.error('Не удалось отправить сообщение')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        raise Exception(f'Ошибка при запросе к API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        raise Exception(f'Ошибка {status_code}')
    try:
        return response.json()
    except ValueError:
        raise ValueError('Ошибка парсинга ответа из формата json')


def check_response(response):
    """Проверяет ответ API."""
    if type(response) is not dict:
        raise TypeError('Ответ API отличен от словаря')
    try:
        list_works = response['homeworks']
    except KeyError:
        raise KeyError('Ошибка словаря по ключу homeworks')
    try:
        homework = list_works[0]
    except IndexError:
        raise IndexError('Список домашних работ пуст')
    return homework


def parse_status(homework):
    """Выбирает из списка конкретную домашнюю работу и ее статус."""
    if 'homework_name' not in homework:
        raise HomeWorkKeyError('Отсутствует ключ "homework_name" в ответе API')
    if 'status' not in homework:
        raise NoKeyInAPIResponseError('Отсутствует ключ "status" в ответе API')
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework_status not in HOMEWORK_STATUSES:
        raise UnknownHomeWorkStatusError(f'Неизвестный статус работы: {homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет токены на валидность."""
    ENV_VARS = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(ENV_VARS):
        print('Отсутствует переменная')
    else:
        return True


def main():
    """Основная логика работы программы."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    STATUS = ''
    if not check_tokens():
        logging.critical('Отсутствуют переменные окружения')
        raise Exception('Отсутствуют переменные окружения')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            message = parse_status(check_response(response))
            if message != STATUS:
                send_message(bot, message)
                STATUS = message
                time.sleep(RETRY_TIME)
        except Exception as error:
            logging.error(f'Сбой в работе программы: {error}')
            send_message(bot, f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
