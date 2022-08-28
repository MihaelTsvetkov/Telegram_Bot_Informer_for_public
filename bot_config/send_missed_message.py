import time
from bot_config.timeperiod import TimePeriod
import logging
from localize.json_translate import get_json_localization

logger = logging.getLogger(__name__)


class SendMissedMessages:
    def __init__(self, telegram_id, config, bot, wait_time, first_messages_amount, last_messages_amount,
                 wait_after_except):
        self.wait_time = wait_time
        self.first_messages_amount = first_messages_amount
        self.last_messages_amount = last_messages_amount
        self.wait_after_except = wait_after_except
        self.telegram_id = telegram_id
        self.config = config
        self.bot = bot

    def check_missed_message_in_time_period_infinite(self, dtnow):
        while True:
            try:
                self.check_missed_message_in_time_period(dtnow)
                time.sleep(self.wait_time)
                pass
            except KeyboardInterrupt:
                logger.info(get_json_localization("polling_stop_keyboard_interrupt"))
                return
            except Exception as e:
                logger.error(f'Smm exception: {type(e).__name__} ', exc_info=True)
            time.sleep(self.wait_after_except)

    def check_missed_message_in_time_period(self, dtnow):
        num_of_missed_messages = self.config.get_missed_messages_counter(self.telegram_id)
        send_message_is_allowed = self.send_message_is_allowed(self.telegram_id, dtnow)
        message_perm_is_allowed = self.message_perm_is_allowed()
        if num_of_missed_messages and send_message_is_allowed and message_perm_is_allowed:
            first_messages, last_messages = self.check_missed_messages(self.telegram_id)
            if first_messages is not None:
                if last_messages is not None:
                    send_message = (f'{get_json_localization("missed_messages_accumulated")}'
                                    f'{num_of_missed_messages} {get_json_localization("missed_messages")}.\n'
                                    f'{get_json_localization("format_missed_messages")}\n'
                                    f'{get_json_localization("First")}'  f"{self.first_messages_amount} " +
                                    f'{get_json_localization("missed_messages")}\n' + f"{' '.join(first_messages)} \n"
                                    f'{get_json_localization("Last")}'  f"{self.last_messages_amount} "
                                    f'{get_json_localization("missed_messages")}: \n '  f"{' '.join(last_messages)}")
                    self.bot.send_message(self.telegram_id, send_message)
                    logger.info(send_message + '\n' f"user_id: {self.telegram_id}")
                else:
                    send_message = (f'{get_json_localization("missed_messages_accumulated")}'
                                    f'{num_of_missed_messages} {get_json_localization("missed_messages")}.\n'
                                    f'{get_json_localization("format_missed_messages")}\n'
                                    f"{' '.join(first_messages)}")
                    self.bot.send_message(self.telegram_id, send_message)
                    logger.info(send_message + '\n' +
                                f"user_id: {self.telegram_id}")
                self.config.clear_missed_message(self.telegram_id)

    def send_message_is_allowed(self, telegram_id, dtnow):
        from_hour, to_hour = self.config.get_time_period(telegram_id)
        time_period = TimePeriod(from_hour, to_hour)
        result = time_period.is_time_inside(dtnow)
        return result

    def message_perm_is_allowed(self):
        inform = self.config.get_ability_to_send_messages(self.telegram_id)
        return inform != 0

    def get_messages_as_dict(self, sort):
        missed_message = dict()
        for row in sort:
            source_topic, message, message_time = row
            str_message_time = str(message_time)
            missed_message.setdefault(source_topic, []).append(message + ': ' + str_message_time)
        pre_output = []
        output = []
        for source_topic in missed_message.keys():
            num_list_of_messages = []
            num = 0
            list_of_messages = missed_message[source_topic]
            for message in list_of_messages:
                num += 1
                num_list_of_messages.append(str(num) + '. ' + message)
            pre_output.append(source_topic + ': ' + '\n' + '\n'.join(num_list_of_messages) + '\n')
        self.config.clear_missed_message(self.telegram_id)
        for items in pre_output:
            output.append(items)
        return output

    def check_missed_messages(self, telegram_id):
        missed_messages = self.config.get_missed_sources_and_topics_and_messages(telegram_id)
        sort = []
        for values in missed_messages:
            sort.append(values)
        show_missed_messages = self.first_messages_amount + self.last_messages_amount
        if len(sort) <= show_missed_messages:
            output = self.get_messages_as_dict(sort)
            return output, None
        else:
            first_messages = sort[0:self.first_messages_amount]
            last_messages = sort[-self.last_messages_amount:]
            output = self.get_messages_as_dict(first_messages)
            output2 = self.get_messages_as_dict(last_messages)
            return output, output2


