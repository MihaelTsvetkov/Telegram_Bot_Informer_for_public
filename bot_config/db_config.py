from db.data_base import Database1


class Config:
    def __init__(self, db: Database1):
        self.db = db

    def get_users(self):
        return self.db.get_user_config()

    def get_message_counter(self, telegram_id):
        return self.db.get_message_counter(telegram_id)

    def get_sources_and_topics_for_check(self):
        return self.db.get_sources_and_topics_for_check()

    def get_user_sources_and_topics_for_check(self, telegram_id):
        return self.db.get_user_sources_and_topics_for_check(telegram_id)

    def set_message_counter(self, counter, telegram_id):
        return self.db.set_message_counter(counter, telegram_id)

    def set_user_topic_and_source(self, source, topic, telegram_id):
        return self.db.set_user_topic_and_source(source, topic, telegram_id)

    def delete_user_topic_and_source(self, source, topic, telegram_id):
        return self.db.delete_user_topic_and_source(source, topic, telegram_id)

    def get_topics(self):
        return self.db.get_topics()

    def get_sources_and_topics(self):
        return self.db.get_sources_and_topics()

    def set_user_name(self, telegram_id, username):
        return self.db.set_user_name(telegram_id, username)

    def set_chat_name(self, telegram_id, chat_name):
        return self.db.set_chat_name(telegram_id, chat_name)

    def add_block_users(self, telegram_id, block):
        return self.db.add_block_users(telegram_id, block)

    def get_block_users(self, telegram_id):
        return self.db.get_block_users(telegram_id)

    def get_source(self):
        return self.db.get_sources()

    def set_password(self, telegram_id, pass_check):
        return self.db.set_password(telegram_id, pass_check)

    def get_password(self, telegram_id):
        return self.db.get_password(telegram_id)

    def get_user_topics_sources(self, telegram_id):
        return self.db.get_user_topics_sources(telegram_id)

    def get_user_sources_and_topics(self, telegram_id):
        return self.db.get_user_sources_and_topics(telegram_id)

    def get_user_sources(self, telegram_id):
        return self.db.get_user_sources(telegram_id)

    def delete_all_subscriptions(self, telegram_id):
        return self.db.delete_all_subscriptions(telegram_id)

    def delete_user_sending_time_period(self, telegram_id, ):
        return self.db.delete_user_sending_time_period(telegram_id, )

    def get_user_topics(self, telegram_id):
        return self.db.get_user_topics(telegram_id)

    def set_user_topic(self, telegram_id):
        return self.db.set_user_topic(telegram_id)

    def set_user_source(self, user_source):
        return self.db.set_user_source(user_source)

    def set_user_data(self, telegram_id, time_from, time_to):
        return self.db.set_user_data(telegram_id, time_from, time_to)

    def get_time_period(self, telegram_id):
        return self.db.get_time_period(telegram_id)

    def get_chat_name(self, telegram_id):
        return self.db.get_chat_name(telegram_id)

    def get_user_name(self, telegram_id):
        return self.db.get_user_name(telegram_id)

    def set_last_msg_dt(self, last_msg_dt, telegram_id):
        return self.db.set_last_msg_dt(last_msg_dt, telegram_id)

    def get_last_msg_dt(self, telegram_id):
        return self.db.get_last_msg_dt(telegram_id)

    def set_missed_message_time_period(self, source_topic, message, telegram_id, time):
        return self.db.set_missed_message_time_period(source_topic, message, telegram_id, time)

    def get_missed_sources_and_topics_and_messages(self, telegram_id):
        return self.db.get_missed_sources_and_topics_and_messages(telegram_id)

    def get_missed_messages_counter(self, telegram_id):
        return self.db.get_missed_messages_counter(telegram_id)

    def set_ability_to_send_message(self, telegram_id, ability_to_send):
        return self.db.set_ability_to_send_message(telegram_id, ability_to_send)

    def clear_ability_to_send_message(self, telegram_id):
        return self.db.clear_ability_to_send_message(telegram_id)

    def get_ability_to_send_messages(self, telegram_id):
        return self.db.get_ability_to_send_messages(telegram_id)

    def get_telegram_id(self):
        return self.db.get_telegram_id()

    def clear_missed_message(self, telegram_id):
        return self.db.clear_missed_message(telegram_id)

    def get_last_user_source(self):
        return

    def get_last_user_topics(self):
        return
