import datetime
import unittest
from bot_config.send_missed_message import SendMissedMessages


class BotMock:
    def __init__(self):
        self.message_is_send = False

    def send_message(self, chat_id, text):
        self.message_is_send = True
        return None


class Config:
    def __init__(self, counter, time_period: tuple[int, int], ability_to_send_messages,
                 source_topic_message_and_time, dt):
        self.counter = counter
        self.time_period = time_period
        self.ability_to_send_messages = ability_to_send_messages
        self.source_topic_message_and_time = source_topic_message_and_time
        self.dt = dt

    def get_missed_messages_counter(self, telegram_id):
        return self.counter

    def clear_missed_message(self, telegram_id):
        return None

    def get_time_period(self, telegram_id):
        return self.time_period

    def get_ability_to_send_messages(self, telegram_id):
        return self.ability_to_send_messages

    def get_missed_sources_and_topics_and_messages(self, telegram_id):
        return self.source_topic_message_and_time

    def get_last_msg_dt(self, telegram_id):
        return self.dt

    def get_dt(self, telegram_id):
        return self.dt


class TestSendMissedMessages(unittest.TestCase):
    def create_config(self):
        time_period = 3, 4
        source_topic_message_and_time = [('s1 t1', 'm1', '12-04-2022: 15:04')]
        return Config(counter=4, time_period=time_period, ability_to_send_messages=1,
                      source_topic_message_and_time=source_topic_message_and_time,
                      dt=datetime.datetime(2022, 7, 23, 16, 7, 12))

    def create_smm(self, config, bot):
        return SendMissedMessages(telegram_id=765487455, config=config, bot=bot, wait_time=5, first_messages_amount=2,
                                  last_messages_amount=2, wait_after_except=5)

    def test_check_missed_message_in_time_period_non_sending_period(self):
        bot = BotMock()
        config = self.create_config()
        smm = self.create_smm(config, bot)
        smm.check_missed_message_in_time_period(datetime.datetime(2022, 7, 23, 16, 7, 12))
        assert not bot.message_is_send

    def test_check_missed_message_in_time_period_sending_period(self):
        bot = BotMock()
        config = self.create_config()
        config.time_period = 19, 23
        smm = self.create_smm(config, bot)
        smm.check_missed_message_in_time_period(datetime.datetime(2022, 7, 23, 20, 7, 12))
        assert bot.message_is_send

    def test_return_values_when_splitting_messages(self):
        bot = BotMock()
        config = self.create_config()
        config.time_period = 19, 23
        config.source_topic_message_and_time = [('s1 t1', 'm1', '12-04-2022: 15:04'),
                                                ('s2 t2', 'm2', '12-04-2022: 15:04'),
                                                ('s3 t3', 'm3', '12-04-2022: 15:04'),
                                                ('s4 t4', 'm4', '12-04-2022: 15:04'),
                                                ('s5 t5', 'm5', '12-04-2022: 15:04')]
        smm = self.create_smm(config, bot)
        smm.check_missed_message_in_time_period(datetime.datetime(2022, 7, 23, 20, 7, 12))
        list1, list2 = smm.check_missed_messages(smm.telegram_id)
        assert len(list1 + list2) == smm.first_messages_amount + smm.last_messages_amount

    def test_return_values_when_messages_not_splitting(self):
        bot = BotMock()
        config = self.create_config()
        config.time_period = 19, 23
        config.source_topic_message_and_time = [('s1 t1', 'm1', '12-04-2022: 15:04'),
                                                ('s2 t2', 'm2', '12-04-2022: 15:04')]
        smm = self.create_smm(config, bot)
        smm.check_missed_message_in_time_period(datetime.datetime(2022, 7, 23, 20, 7, 12))
        assert len(smm.check_missed_messages(smm.telegram_id)) == smm.first_messages_amount


def main():
    TestSendMissedMessages()


if __name__ == "__main__":
    unittest.main()
