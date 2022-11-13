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


class APIRequestError(Error):
    """Ошибка при запросе к API."""
    pass


class StatusError(Error):
    """Ошибка в статусе."""
    pass


class StatusError(Error):
    """Ошибка в статусе."""
    pass


class AnswerJsonError(ValueError):
    """Ошибка парсинга ответа из формата json."""
    pass


class HomeWorkDictionaryError(KeyError):
    """Ошибка словаря по ключу homeworks."""
    pass


class HomeWorkKeyError(KeyError):
    """Отсутствует ключ "homework_name" в ответе API."""
    pass


class APIResponseDifferentDictionary(TypeError):
    """Ответ API отличен от словаря."""
    pass


class HomeworkListEmpty(IndexError):
    """Список домашних работ пуст."""
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
    except APIRequestError as error:
        raise APIRequestError(f'Ошибка при запросе к API: {error}')
    if response.status_code != HTTPStatus.OK:
        status_code = response.status_code
        raise StatusError(f'Ошибка {status_code}')
    try:
        return response.json()
    except AnswerJsonError:
        raise AnswerJsonError('Ошибка парсинга ответа из формата json')


def check_response(response):
    """Проверяет ответ API."""
    if type(response) is not dict:
        raise APIResponseDifferentDictionary('Ответ API отличен от словаря')
    try:
        list_works = response['homeworks']
    except HomeWorkDictionaryError:
        raise HomeWorkDictionaryError('Ошибка словаря по ключу homeworks')
    try:
        homework = list_works[0]
    except HomeworkListEmpty:
        raise HomeworkListEmpty('Список домашних работ пуст')
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
        raise UnknownHomeWorkStatusError(f'Неизвестный статус работы:'
                                         f'{homework_status}')
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
