from bot_config.timeperiod import TimePeriod
from bot_config.checksub import CheckSub
import datetime
import logging
from localize.json_translate import get_json_localization

logger = logging.getLogger(__name__)


class CheckBeforeSend:
    def __init__(self, config, bot):
        self.config = config
        self.bot = bot
        self.mes_counter = 0

    def checking_telegram_id(self, topic, source, message, send_message, time):
        db_telegram_id = self.config.get_telegram_id()
        for telegram_id in db_telegram_id:
            result_subscribe = self.checking_subscribes(telegram_id, topic, source)
            logger.info(f'{get_json_localization("check_user_subscriptions")} {telegram_id} '
                        f'{get_json_localization("with_incoming_message")},'
                        f' {get_json_localization("result")}: {result_subscribe}')
            result_period = self.checking_time_period(telegram_id)
            logger.info(f'{get_json_localization("check_user_time_period")}'
                        f'{get_json_localization("to_which_messages_can_be_sent")} {telegram_id}, '
                        f'{get_json_localization("result")}: {result_period}')

            if not result_subscribe:
                pass
            elif not result_period:
                source_topic = '{}/{}'.format(source, topic)
                self.config.set_missed_message_time_period(source_topic, message, telegram_id, time)
                logger.info(f'{get_json_localization("write_missed_message_due_to_time_period")}'
                            f'{source_topic}, {get_json_localization("message")}{message}: '
                            f'{get_json_localization("time")}{time}'
                            + ' ' + 'user_id')
            else:
                db_user_name = self.config.get_user_name(telegram_id)
                db_chat_name = self.config.get_chat_name(telegram_id)
                self.bot.send_message(telegram_id, send_message)
                if not db_chat_name:
                    logger.info(f'{get_json_localization("message")} {send_message}. '
                                f'{get_json_localization("send_to_client")}: {db_user_name},'
                                f' user_id: {telegram_id} ')
                else:
                    logger.info(f'{get_json_localization("message")} {send_message}. '
                                f'{get_json_localization("send_to_client")}: {db_chat_name},'
                                f' user_id: {telegram_id} ')

    def checking_subscribes(self, telegram_id, topic, source):
        user_source_topic = self.config.get_user_topics_sources(telegram_id)
        inform = self.config.get_ability_to_send_messages(telegram_id)
        check_sub = CheckSub(user_source_topic, inform)
        result = check_sub.check_the_values(topic, source)
        return result

    def checking_time_period(self, telegram_id):
        from_hour, to_hour = self.config.get_time_period(telegram_id)
        time_check = TimePeriod(from_hour, to_hour)
        result_time_check = time_check.is_time_inside(datetime.datetime.now())
        return result_time_check

    def report_send_message(self, is_same_period, dtnow, telegram_id):
        if is_same_period:
            counter = self.config.get_message_counter(telegram_id) or 0
            counter += 1
        else:
            counter = 1
        self.config.set_message_counter(counter, telegram_id)
        self.config.set_last_msg_dt(dtnow, telegram_id)
