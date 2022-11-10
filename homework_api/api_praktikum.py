from dotenv import load_dotenv
import os
import requests

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
payload = {'from_date': 0}
# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)
# Печатаем ответ API в формате JSON
print(homework_statuses.text)
