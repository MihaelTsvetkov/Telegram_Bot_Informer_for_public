import time
from bot_config.check_before_send import CheckBeforeSend
# noinspection PyPackageRequirements
from telebot.apihelper import ApiTelegramException
import logging
import json


logger = logging.getLogger(__name__)


def worker(config, bot, qu, wait_after_except):
    check_before_send = CheckBeforeSend(config, bot)
    while True:
        try:
            logger.info(f'Kоличество элементов в очереди на прием: {qu.num_of_mes()} ')
            item = qu.get()

            topic = item.topic

            source = item.source

            text = item.text

            text_to_send = (
                '{}/{}: {} \n[{}]'.format(source, topic, text, item.time))
            check_before_send.checking_telegram_id(topic, source, text, text_to_send, item.time)
            qu.task_done()
        except KeyboardInterrupt:
            logger.info('Завершение работы worker, причина: KeyboardInterrupt')
            return
        except ApiTelegramException:
            wait_time = 60
            logger.error(f'Превышен лимит отправки сообщений в телеграм, ждем {wait_time} секунд')
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f'Worker exception: {type(e).__name__} ', exc_info=True)
            time.sleep(wait_after_except)
