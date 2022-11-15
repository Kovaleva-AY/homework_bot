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


class StatusCodeError(Error):
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
