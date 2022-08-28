import unittest
from bot_config.fsm import FSM
from db.convert import output_sources_and_topics
from localize.json_translate import get_json_localization


def process_message(message):
    return


class BotMock:
    def __init__(self):
        self.subscription_error = False
        self.call_send_message = False
        self.topic_error = False
        self.source_error = False

    def reply_to(self, message, text: str, **kwargs):
        return None

    def send_message(self, chat_id, text):
        self.call_send_message = True
        if text == get_json_localization("topic_not_exist"):
            self.topic_error = True
        if text == get_json_localization("source_not_exist"):
            self.source_error = True
        if text == get_json_localization("source&topic_not_exist"):
            self.subscription_error = True
        return None


class ConfigMock:
    def __init__(self, source_and_topic, user_source_and_topic, time_period,
                 ability_to_send_messages, source, topic, source_and_topic_for_check,
                 user_source, user_topic, user_source_and_topic_for_check,
                 ):

        self.source_and_topic = source_and_topic
        self.user_source_and_topic = user_source_and_topic
        self.time_period = time_period
        self.ability_to_send_messages = ability_to_send_messages
        self.source = source
        self.topic = topic
        self.source_and_topic_for_check = source_and_topic_for_check
        self.user_source = user_source
        self.user_topic = user_topic
        self.user_source_and_topic_for_check = user_source_and_topic_for_check

    def get_sources_and_topics(self):
        return self.source_and_topic

    def get_user_sources_and_topics(self, telegram_id):
        return self.user_source_and_topic

    def get_time_period(self, telegram_id):
        return self.time_period

    def get_ability_to_send_messages(self, telegram_id):
        return self.ability_to_send_messages

    def get_source(self):
        return self.source

    def get_topics(self):
        return self.topic

    def get_sources_and_topics_for_check(self):
        return self.source_and_topic_for_check

    def get_user_sources(self, telegram_id):
        return self.user_source

    def get_user_topics(self, telegram_id):
        return self.user_topic

    def get_user_sources_and_topics_for_check(self, telegram_id):
        return self.user_source_and_topic_for_check

    def delete_user_topic_and_source(self, source, topic, telegram_id):
        return None


class Message:
    def __init__(self, chat, text):
        self.chat = chat
        self.text = text


class Chat:
    def __init__(self, id: int):
        self.id = id


class TestFsm(unittest.TestCase):
    def create_config(self):
        config = ConfigMock(source_and_topic={'s1': 't1'}, user_source_and_topic={'s1': 't1'}, time_period=12-1,
                            ability_to_send_messages=1, source='s1', topic='t1',
                            source_and_topic_for_check='s1t1', user_source=[('s1',)], user_topic=[('t1',)],
                            user_source_and_topic_for_check=[('s1', 't1')])
        return config

    def create_fsm(self, bot, config):
        return FSM(bot, process_message(message='message'), config, password="12345",
                   count_authorization=4)

    def test_get_available_sources_topics_1_item(self):
        config = self.create_config()
        bot = BotMock()
        fsm = self.create_fsm(bot, config)
        result = fsm.get_available_sources_topics()
        assert result == output_sources_and_topics(config.source_and_topic)

    def test_get_available_sources_topics_no_items(self):
        source_topic = []
        config = self.create_config()
        config.source_and_topic = source_topic
        config.user_source = []
        bot = BotMock()
        fsm = self.create_fsm(bot, config)
        result = fsm.get_available_sources_topics()
        assert not result

    def test3(self):
        bot = BotMock()
        fsm = self.create_fsm(bot, self.create_config())
        fsm.change_state(fsm.state_authorization)
        assert fsm.state == fsm.state_authorization

    def test4(self):
        config = self.create_config()
        config.time_period = 12, 1
        bot = BotMock()
        fsm = self.create_fsm(bot, config)
        assert fsm.get_user_configuration(telegram_id=434234543) is not None

    def test5(self):
        config = self.create_config()
        config.time_period = None, None
        config.ability_to_send_messages = 0
        bot = BotMock()
        fsm = self.create_fsm(bot, config)
        assert fsm.get_user_configuration(telegram_id=434234543) == get_json_localization("user_has_not_set_values")

    def test7(self):
        bot = BotMock()
        fsm = self.create_fsm(bot, self.create_config())
        fsm.send_message(chat_id=54232343, text_to_send='some_text')
        assert bot.call_send_message

    def test8(self):
        bot = BotMock()
        fsm = self.create_fsm(bot, self.create_config())
        message = Message(chat=Chat(id=43242345), text='s3')
        assert fsm.state_unsubscribe(message=message) is None

    def test9(self):
        bot = BotMock()
        config = self.create_config()
        fsm = self.create_fsm(bot, config)
        source_topic = 's1/t1'
        message = Message(chat=Chat(id=43242345), text=source_topic)
        assert fsm.state_unsubscribe(message=message)

    def test10(self):
        bot = BotMock()
        user_source_topic = dict()
        user_source_topic.setdefault('s1', []).append('t1')
        config = self.create_config()
        config.user_source_topic = user_source_topic
        fsm = self.create_fsm(bot, config)
        source_topic = 's1/t4'
        message = Message(chat=Chat(id=43242345), text=source_topic)
        fsm.state_unsubscribe(message=message)
        assert bot.topic_error

    def test11(self):
        bot = BotMock()
        user_source_topic = dict()
        user_source_topic.setdefault('s1', []).append('t1')
        config = self.create_config()
        config.user_source_topic = user_source_topic
        fsm = self.create_fsm(bot, config)
        source_topic = 's4/t1'
        message = Message(chat=Chat(id=43242345), text=source_topic)
        fsm.state_unsubscribe(message=message)
        assert bot.source_error


def main():
    TestFsm()


if __name__ == "__main__":
    unittest.main()
