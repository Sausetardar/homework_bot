import os
from dotenv import load_dotenv
import requests
import logging
import time
import telegram
from logging.handlers import RotatingFileHandler

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filename='logs.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'logs.log', maxBytes=50000000, backupCount=5, encoding='utf-8'
)
logger.addHandler(handler)

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


def send_message(bot, message):
    """Отправляет пользователю сообщение со статусом домашней работы."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logger.info('Сообщение отправлено:)')
    except telegram.TelegramError as error:
        information = f'Сообщение не отправлено, {error}'
        logger.error(information)
        raise information


def get_api_answer(current_timestamp):
    """Делает запрос к API-сервису Яндекс.Домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        api_answer = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except Exception as error:
        information = f'Сбой в работе программы: {error}'
        logger.error(information)
        raise information
    if api_answer.status_code != requests.codes.ok:
        inf = f'Ответ сервера недоступен. Код ошибки {api_answer.status_code}'
        logger.error(inf)
        raise inf
    return api_answer.json()


def check_response(response):
    """Проверяет корректность данных API-сервиса Яндекс.Домашка."""
    try:
        homework = response['homeworks']
        response['current_date']
    except KeyError:
        information = 'Отсутствует один из ключей'
        logger.error(information)
        raise information
    else:
        if not isinstance(homework, list):
            information = 'Передан тип данных, не являющийся словарем'
            logger.error(information)
            raise information
    if homework == []:
        logger.debug('Новых изменений нет')
    return homework


def parse_status(homework):
    """Отбирает необходимые данные для формирования сообщения."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as error:
        information = f'Нет ключа {error}'
        logger.error(information)
        raise KeyError(information)

    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет наличие всех необходимых переменных окружения."""
    DOTENVS = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    for key, value in DOTENVS.items():
        if not value:
            logger.critical(
                f'Отсутствует обязательная переменная окружения: {key}'
            )
            return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            if response.get('homeworks'):
                send_message(bot, parse_status(response.get('homeworks')))
                current_timestamp = response.get(
                    'current_date', current_timestamp
                )

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            send_message(message, bot)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
