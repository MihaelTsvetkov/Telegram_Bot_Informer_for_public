import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import datetime
from urllib.parse import urlparse, parse_qs
import threading
import options.log_settings
import queue_config.message_queue
from queue_config.message import Message
from bot_config.worker import worker
from bot_config.send_missed_message import SendMissedMessages
from bot_config.bot import TelegramBot
from options import settings
import logging

logger = logging.getLogger(__name__)

qu = queue_config.message_queue.MessageQueue()
message = ['source', 'topic', 'message']


class BotWorker(threading.Thread):
    def __init__(self, telegram_bot, config):
        super().__init__()
        self.telegram_bot = telegram_bot
        self.config = config

    def run(self):
        worker(self.telegram_bot, self.config, qu, settings.WAIT_AFTER_EXCEPTION)


class PollingThread(threading.Thread):
    def __init__(self, telegram_bot):
        super().__init__()
        self.telegram_bot = telegram_bot

    def run(self):
        telegram_bot = self.telegram_bot
        telegram_bot.polling(settings.WAIT_AFTER_EXCEPTION)


class MissedTimeMessage(threading.Thread):
    def __init__(self, telegram_id, bot, config):
        super().__init__()
        self.telegram_id = telegram_id
        self.bot = bot
        self.config = config

    def run(self):
        slm = SendMissedMessages(self.telegram_id, self.config, self.bot, settings.WAIT_TIME_TO_MISSED_MESSAGES,
                                 settings.FIRST_MISSED_MESSAGES, settings.LAST_MISSED_MESSAGES,
                                 settings.WAIT_AFTER_EXCEPTION)
        slm.check_missed_message_in_time_period_infinite(datetime.datetime.now())


class GetTgId(threading.Thread):
    def __init__(self, telegram_bot, config):
        super().__init__()
        self.telegram_bot = telegram_bot
        self.config = config

    def run(self):
        exists_telegram_id = []
        while True:
            telegram_bot = self.telegram_bot
            list_of_telegram_id = telegram_bot.get_telegram_id()
            time.sleep(settings.WAIT_TIME_TO_MISSED_MESSAGES)
            for telegram_id in list_of_telegram_id:
                if telegram_id in exists_telegram_id:
                    pass
                else:
                    run_missed_time_message(telegram_id, self.telegram_bot, self.config)
                    exists_telegram_id.append(telegram_id)
                    time.sleep(settings.WAIT_TIME_TO_MISSED_MESSAGES)


def run_get_telegram_id(telegram_bot, config):
    tp = GetTgId(telegram_bot, config)
    tp.name = 'Get_Telegram_Id_Thread'
    tp.start()


def run_worker(telegram_bot, config):
    tp = BotWorker(telegram_bot, config)
    tp.name = 'Bot_Worker_Thread'
    tp.start()


def run_polling(telegram_bot):
    tp = PollingThread(telegram_bot)
    tp.name = "Polling_Thread"
    tp.start()


def run_missed_time_message(telegram_id, bot, config):
    tp = MissedTimeMessage(telegram_id, bot, config)
    tp.name = 'Missed_Time_Message_Thread'
    tp.start()


class RequestHandler(BaseHTTPRequestHandler):
    def send_min_response(self, code, report=None):
        self.log_request(code)
        self.send_response_only(code, report)

    # noinspection PyPep8Naming
    def do_POST(self):
        if self.path == '/favicon.ico':
            self.send_min_response(200, 'OK')
            self.send_header('Content-type', 'html')
            self.end_headers()

        elif self.path.startswith(f'/{settings.TOKEN_URL}/message'):
            query_components = parse_qs(urlparse(self.path).query)
            if 'source' not in query_components:
                self.send_min_response(400, 'error')
                self.end_headers()
                return
            if 'topic' not in query_components:
                self.send_min_response(400, 'error')
                self.end_headers()
                return
            if 'message' not in query_components:
                self.send_min_response(400, 'error')
                self.end_headers()
                return
            self.send_min_response(200, 'OK')
            self.end_headers()
            source = query_components["source"]
            topic = query_components["topic"]
            text = query_components["message"]
            now_time = datetime.datetime.now()
            mes = Message(now_time, source[0], topic[0], text[0])
            qu.put(mes)
            logger.debug(f'количество элементов в очереди на отправку: {qu.num_of_mes()} ')

        else:
            self.send_min_response(404, 'error')
            self.end_headers()


def setup_logging(level):
    options.log_settings.setup_logging(level, settings.DEBUG_FILE_PATH, settings.INFO_FILE_PATH)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)


def main():
    try:
        telegram_bot = TelegramBot(settings.API_TOKEN, settings.PASSWORD, settings.COUNT_AUTH, settings.DATABASE_HOST,
                                   settings.DATABASE_USER, settings.DATABASE_PASSWD,
                                   settings.DATABASE_PORT, settings.DATABASE, settings.WAIT_TIME_TO_MISSED_MESSAGES,
                                   settings.LENGTH_SOURCE, settings.LENGTH_TOPIC, settings.LENGTH_SOURCE_TOPIC,
                                   settings.LENGTH_MESSAGE)
        db_config = telegram_bot.get_config()
        run_worker(db_config, telegram_bot)
        run_polling(telegram_bot)
        run_get_telegram_id(telegram_bot, db_config)
        setup_logging(settings.LOGGING_LEVEL)
        server_address = ("", settings.SERVER_PORT)
        httpd = HTTPServer(server_address, RequestHandler)
        httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, certfile=settings.SSL_CERTIFICATE_PATH,
                                       keyfile=settings.SSL_KEY_PATH,
                                       ssl_version=ssl.PROTOCOL_TLS)
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('Shutdown')

    except Exception as e:
        logger.error(f'Main exception: {type(e).__name__} ', exc_info=True)
        raise e


if __name__ == '__main__':
    main()
