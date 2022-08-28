import datetime
from typing import Optional
from bot_config.utils import parse_time_period,  WrongHour, parse_subscribe
import time
import bot_config.list_of_allowed_values as lists
# noinspection PyPackageRequirements
from telebot import types
from bot_config.authorized import Authorized
from db.convert import output_sources_and_topics
import logging
from localize.json_translate import get_json_localization


logger = logging.getLogger(__name__)


def get_telegram_id(message):
    telegram_id = message.chat.id
    return telegram_id


def find_username(username, first_name, last_name) -> str:
    if username is None:
        if first_name is None:
            return last_name
        if last_name is None:
            return first_name
        else:
            return first_name + ' ' + last_name
    else:
        return username


def get_time_with_utc_offset_as_str():
    """ :return current time and timezone """
    dt_now = datetime.datetime.now().replace(microsecond=0)
    timezone = datetime.timezone(dt_now.astimezone().utcoffset())
    return f"{dt_now} ({timezone})"


class FSM:
    def __init__(self, bot, process_message, config, password, count_authorization):
        self.state = None
        self.bot = bot
        self.config = config
        self.process_message = process_message
        self.password = password
        self.count_authorization = count_authorization
        self.count_auth = 0

    def show_available_subscriptions(self, message) -> bool:
        """ :return if subscriptions are available """
        dict_of_source_and_topics = self.config.get_sources_and_topics()
        if not dict_of_source_and_topics:
            self.send_message(message.chat.id, str(get_json_localization("empty_database")))
            return False
        else:
            output = output_sources_and_topics(dict_of_source_and_topics)
            send_message = str(get_json_localization("available_sources&topics")) + ' \n{}'.format(output)
            self.send_message_with_keyboard(message.chat.id, send_message,
                                            get_json_localization("subscribe_button"),
                                            get_json_localization("back_button"))
            return True

    def get_available_sources_topics(self):
        dict_of_source_and_topics = self.config.get_sources_and_topics()
        return output_sources_and_topics(dict_of_source_and_topics)

    def show_user_subscriptions(self, message) -> Optional[dict]:
        """ :return if user has subscriptions """
        dict_user_source_topics = self.config.get_user_sources_and_topics(get_telegram_id(message))
        if not dict_user_source_topics:
            self.reply_to_message(message, str(get_json_localization("user_has_no_subscriptions")))
            return None

        output = output_sources_and_topics(dict_user_source_topics)
        send_message = str(get_json_localization("user_sources&topics")) + f' \n{output}'
        self.send_message(message.chat.id, send_message)
        return output_sources_and_topics(dict_user_source_topics)

    def change_state(self, new_state):
        initial_state_name = self.state.__name__ if self.state is not None else "None"
        new_state_name = new_state.__name__ if new_state is not None else "None"
        logger.debug(f'{initial_state_name} -> {new_state_name}')
        self.state = new_state

    def get_user_configuration(self, telegram_id):
        time_from, time_to = self.config.get_time_period(telegram_id)
        ability_to_receiving_messages = self.config.get_ability_to_send_messages(telegram_id)
        send_message = ''
        if ability_to_receiving_messages:
            send_message += get_json_localization("receiving_messages") + '\n'
        if time_from and time_to:
            send_message += str(get_json_localization("send_message_from")) + str(time_from) + str(
                get_json_localization("on")) + str(
                time_to) + '\n'
        if send_message == '':
            send_message = str(get_json_localization("user_has_not_set_values"))
        return send_message

    def send_message_with_keyboard(self, chat_id, message, *buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for button in buttons:
            type_button = types.KeyboardButton(button)
            markup.add(type_button)
        self.bot.send_message(chat_id, message, reply_markup=markup, parse_mode='html')
        logger.debug(f'bot_send_message: {message}. User_id: {chat_id}')

    def send_message(self, chat_id, text_to_send):
        self.bot.send_message(chat_id, text_to_send)
        logger.debug(f'bot_send_message: {text_to_send}. User_id: {chat_id}')

    def reply_to_message_with_keyboard(self, message, send_message, *buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for button in buttons:
            type_button = types.KeyboardButton(button)
            markup.add(type_button)
        self.bot.reply_to(message, send_message, reply_markup=markup, parse_mode='html')
        logger.debug(f'bot_send_message: {send_message} User_id: {get_telegram_id(message)}')

    def reply_to_message(self, message, text_to_send):
        self.bot.reply_to(message, text_to_send)
        logger.debug(f'bot-reply: {text_to_send}, User_id: {get_telegram_id(message)}')

    def run(self, message):
        """ run the fsm """
        self.state(message)

    def is_finished(self):
        return self.state is None

    def start_without_password(self):
        logger.debug('Fsm - Run, Current state - state_settings')
        self.state = self.state_settings

    def start(self):
        logger.debug('Fsm - Run, Current state - authorization')
        self.state = self.state_authorization

    def state_authorization(self, message):
        telegram_id = get_telegram_id(message)
        logger.debug(
            f'Function - authorization, Current state - authorization, user_id: {telegram_id}  ')
        start_button_in_auth = 'Старт'
        authorization = Authorized(self.password)
        user_password = message.text
        result_authorization = authorization.check_password(user_password)
        if not result_authorization:
            self.count_auth += 1
            self.bot.reply_to(message, str(get_json_localization("wrong_password")), parse_mode='html')
            logger.debug(f'bot_send_message: {str(get_json_localization("wrong_password"))}, user_id: {telegram_id}, '
                         f'password:{self.password}')

            if self.count_auth >= self.count_authorization:
                send_message = str(get_json_localization("number_of_password_attempts_exceeded"))
                self.send_message(message.chat.id, send_message)
                block = 1
                self.config.add_block_users(telegram_id, block)
                self.state = self.state_for_blocked_users
                return
        else:
            username = find_username(message.from_user.username, message.from_user.first_name,
                                     message.from_user.last_name)
            self.config.set_user_name(telegram_id, username)
            chat_name = message.chat.title
            self.config.set_chat_name(telegram_id, chat_name)
            password_check = '1'
            self.config.set_password(telegram_id, password_check)
            self.send_message_with_keyboard(message.chat.id, str(get_json_localization("access_is_allowed")),
                                            start_button_in_auth)
            self.bot.register_next_step_handler(message, self.process_message)
            self.change_state(self.state_greetings)

    def state_greetings(self, message):
        telegram_id = get_telegram_id(message)
        self.send_message_with_keyboard(message.chat.id, str(get_json_localization("menu")),
                                        get_json_localization("message_button"),
                                        get_json_localization("settings_button"))
        self.change_state(self.state_settings)
        return telegram_id

    def state_for_blocked_users(self, message):
        pass

    def state_settings(self, message):
        user_message = message.text.strip()
        if user_message == get_json_localization("settings_button"):
            self.send_message_with_keyboard(message.chat.id, str(get_json_localization("settings")),
                                            get_json_localization("set_time_button"),
                                            get_json_localization("delete_time_button"),
                                            get_json_localization("show_settings_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_settings_choose)
        elif user_message == get_json_localization("message_button"):
            self.send_message_with_keyboard(message.chat.id, str(get_json_localization("messages")),
                                            get_json_localization("subscribe_inform_button"),
                                            get_json_localization("unsubscribe_inform_button"),
                                            get_json_localization("subscribes_button"),
                                            get_json_localization("user_subscribes_button"),
                                            get_json_localization("unsubscribe_button"),
                                            get_json_localization("unsubscribe_all_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_message_settings)

    def state_settings_choose(self, message):
        telegram_id = get_telegram_id(message)
        user_message = message.text.strip()
        if user_message == get_json_localization("set_time_button"):
            output = get_time_with_utc_offset_as_str() + '\n'
            send_message = output + str(get_json_localization("enter_the_time_to_send_messages"))
            self.reply_to_message_with_keyboard(message, send_message, get_json_localization("back_button"))
            self.change_state(self.state_get_user_time_period)
        elif user_message == get_json_localization("delete_time_button"):
            time_from, time_to = self.config.get_time_period(telegram_id)
            if time_from is None and time_to is None:
                send_message = str(get_json_localization("no_set_value"))
                self.send_message(message.chat.id, send_message)
                return
            elif time_from == [] and time_to == []:
                send_message = str(get_json_localization("no_set_value"))
                self.send_message(message.chat.id, send_message)
                return
            send_message = str(get_json_localization("user_have_set_value")) + str(time_from) + \
                           str(get_json_localization("on")) \
                           + str(time_to) + str(get_json_localization("delete_value"))
            self.send_message_with_keyboard(message.chat.id, send_message,
                                            get_json_localization("confirm_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_prepare_to_delete_time)
        elif user_message == get_json_localization("show_settings_button"):
            output = get_json_localization("current_time") + get_time_with_utc_offset_as_str() + '\n'
            send_message = self.get_user_configuration(telegram_id)
            self.send_message(message.chat.id, output + send_message)
            return
        elif user_message == get_json_localization("back_button"):
            self.reply_to_message_with_keyboard(message, get_json_localization("main_menu"),
                                                get_json_localization("message_button"),
                                                get_json_localization("settings_button"))
            self.change_state(self.state_settings)

    def state_message_settings(self, message):
        telegram_id = get_telegram_id(message)
        logger.debug(
            f'Function: message_settings, user_id: {telegram_id}')
        user_message = message.text.strip()

        if user_message == get_json_localization("subscribes_button"):
            are_subscriptions_available = self.show_available_subscriptions(message)
            if not are_subscriptions_available:
                return
            self.change_state(self.state_subscribe_prepare)

        elif user_message == get_json_localization("back_button"):
            self.reply_to_message_with_keyboard(message, get_json_localization("menu"),
                                                get_json_localization("message_button"),
                                                get_json_localization("settings_button"))
            self.change_state(self.state_settings)

        elif user_message == get_json_localization("user_subscribes_button"):
            self.show_user_subscriptions(message)
            return

        elif user_message == get_json_localization("unsubscribe_all_button"):
            output = self.show_user_subscriptions(message)
            if output is None:
                return
            self.send_message_with_keyboard(message.chat.id, get_json_localization("are_you_sure"),
                                            get_json_localization("confirm_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_unsubscribe_prepare)

        elif user_message == get_json_localization("unsubscribe_button"):
            output = self.show_user_subscriptions(message)
            if output is None:
                return

            reply_message = get_json_localization("enter_the_source&topic_unsubscribe")
            self.send_message_with_keyboard(message.chat.id, reply_message,
                                            get_json_localization("back_button"))
            self.change_state(self.state_unsubscribe)

        elif user_message == get_json_localization("subscribe_inform_button"):
            ability_to_send_messages = 1
            send_message = get_json_localization("enable_receiving_messages")
            self.reply_to_message(message, send_message)
            logger.info(
                get_json_localization("enable_receiving_messages") + f'user_id: {telegram_id}')
            self.config.set_ability_to_send_message(telegram_id, ability_to_send_messages)

        elif user_message == get_json_localization("unsubscribe_inform_button"):
            send_message = get_json_localization("turn_off_receiving_messages")
            self.send_message(message.chat.id, send_message)
            logger.info(
                get_json_localization("turn_off_receiving_messages") + 'user_id: {telegram_id}')
            self.config.clear_ability_to_send_message(telegram_id)

    def state_subscribe_prepare(self, message):
        get_telegram_id(message)
        user_message = message.text.strip()
        if user_message == get_json_localization("subscribe_button"):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
            back_button_in_def = types.KeyboardButton(get_json_localization("back_button"))
            markup.add(back_button_in_def)
            self.send_message_with_keyboard(message.chat.id,
                                            get_json_localization("enter_the_source&topic_subscribe"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_subscribe)

        elif user_message == get_json_localization("back_button"):
            self.send_message_with_keyboard(message.chat.id, get_json_localization("messages"),
                                            get_json_localization("subscribe_inform_button"),
                                            get_json_localization("unsubscribe_inform_button"),
                                            get_json_localization("subscribes_button"),
                                            get_json_localization("user_subscribes_button"),
                                            get_json_localization("unsubscribe_button"),
                                            get_json_localization("unsubscribe_all_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_message_settings)

    def state_subscribe(self, message):
        telegram_id = get_telegram_id(message)
        user_message = message.text.strip()
        user_text = message.text
        get_source = self.config.get_source()
        get_topic = self.config.get_topics()

        if user_message in lists.back:
            self.reply_to_message_with_keyboard(message, get_json_localization("messages"),
                                                get_json_localization("subscribe_inform_button"),
                                                get_json_localization("unsubscribe_inform_button"),
                                                get_json_localization("subscribes_button"),
                                                get_json_localization("user_subscribes_button"),
                                                get_json_localization("unsubscribe_button"),
                                                get_json_localization("unsubscribe_all_button"),
                                                get_json_localization("back_button"))
            self.change_state(self.state_message_settings)
            return

        source, topic = parse_subscribe(user_text)

        get_subscription = self.config.get_sources_and_topics_for_check()
        subscription = (source, topic)
        ability_to_send_messages = self.config.get_ability_to_send_messages(telegram_id)

        if (source,) in get_source and topic == '*':
            self.config.set_user_topic_and_source(source, topic, telegram_id)
            if not ability_to_send_messages:
                send_message = get_json_localization("subscribe_to_all_topics") + source + '.' + \
                               get_json_localization("hint_for_receiving messages")
            else:
                send_message = get_json_localization("subscribe_to_all_topics") + source

            logger.info(
                get_json_localization("subscribe_to_topics") + source + f'user_id: {telegram_id},'
                                                                        f' subscribe -> message_settings')
            self.reply_to_message_with_keyboard(message, send_message, get_json_localization("subscribe_inform_button"),
                                                get_json_localization("unsubscribe_inform_button"),
                                                get_json_localization("subscribes_button"),
                                                get_json_localization("user_subscribes_button"),
                                                get_json_localization("unsubscribe_button"),
                                                get_json_localization("unsubscribe_all_button"),
                                                get_json_localization("back_button"))
            self.show_user_subscriptions(message)
            self.change_state(self.state_message_settings)
            return

        if topic is None:
            send_message = get_json_localization("incorrect_format")
            self.send_message(message.chat.id, send_message)
            return

        if (source,) not in get_source:
            send_message = get_json_localization("source_not_exist")
            self.send_message(message.chat.id, send_message)
            self.send_message(message.chat.id, self.get_available_sources_topics())
            return

        if (topic,) not in get_topic:
            send_message = get_json_localization("topic_not_exist")
            self.send_message(message.chat.id, send_message)
            self.send_message(message.chat.id, self.get_available_sources_topics())
            return

        if subscription not in get_subscription:
            send_message = get_json_localization("source&topic_not_exist")
            self.send_message(message.chat.id, send_message)
            return

        self.config.set_user_topic_and_source(source, topic, telegram_id)
        if not ability_to_send_messages:
            send_message = get_json_localization("subscribe_to_source&topic") + f'{source}/{topic}.' + \
                           get_json_localization(
                               "hint_for_receiving messages")
        else:
            send_message = get_json_localization("subscribe_to_source&topic") + f'{source}/{topic}.'
        logger.info(
            get_json_localization("subscribe_to_source") + f'{source},' + get_json_localization("topic") +
            f'{topic}, user_id: {telegram_id},'
            f' subscribe -> message_settings')
        self.reply_to_message_with_keyboard(message, send_message, get_json_localization("subscribe_inform_button"),
                                            get_json_localization("unsubscribe_inform_button"),
                                            get_json_localization("subscribes_button"),
                                            get_json_localization("user_subscribes_button"),
                                            get_json_localization("unsubscribe_button"),
                                            get_json_localization("unsubscribe_all_button"),
                                            get_json_localization("back_button"))
        self.show_user_subscriptions(message)
        self.change_state(self.state_message_settings)
        return source, topic

    def state_unsubscribe(self, message):
        telegram_id = get_telegram_id(message)
        user_message = message.text.strip()
        get_user_source = self.config.get_user_sources(telegram_id)
        get_user_topic = self.config.get_user_topics(telegram_id)

        if user_message in lists.back:
            self.reply_to_message_with_keyboard(message, get_json_localization("messages"),
                                                get_json_localization("subscribe_inform_button"),
                                                get_json_localization("unsubscribe_inform_button"),
                                                get_json_localization("subscribes_button"),
                                                get_json_localization("user_subscribes_button"),
                                                get_json_localization("unsubscribe_button"),
                                                get_json_localization("unsubscribe_all_button"),
                                                get_json_localization("back_button"))
            self.change_state(self.state_message_settings)
            return

        source, topic = parse_subscribe(user_message)
        get_subscription = self.config.get_user_sources_and_topics_for_check(telegram_id)
        subscription = (source, topic)
        ability_to_send_messages = self.config.get_ability_to_send_messages(telegram_id)

        if topic is None:
            send_message = get_json_localization("incorrect_input_format")
            self.send_message(message.chat.id, send_message)
            return

        if (source, ) not in get_user_source:
            send_message = get_json_localization("source_not_exist")
            self.send_message(message.chat.id, send_message)
            self.send_message(message.chat.id, self.get_available_sources_topics())
            return

        if (topic,) not in get_user_topic:
            send_message = get_json_localization("topic_not_exist")
            self.send_message(message.chat.id, send_message)
            self.send_message(message.chat.id, self.get_available_sources_topics())
            return

        if subscription not in get_subscription:
            send_message = get_json_localization("source&topic_not_exist")
            self.send_message(message.chat.id, send_message)
            return

        self.config.delete_user_topic_and_source(source, topic, telegram_id)
        if not ability_to_send_messages:
            send_message = get_json_localization("unsubscribe_from_source&topic") + f'{source}/{topic}.' + \
                           get_json_localization("hint_for_receiving messages")
        else:
            send_message = get_json_localization("unsubscribe_from_source&topic") + f'{source}/{topic}.'
        logger.info(
            get_json_localization("unsubscribe_from_source") + f'{source},' +
            get_json_localization("topics") + f'{topic}, '
                                              f'user_id: {telegram_id},'
                                              f' subscribe -> '
                                              f'message_settings')
        self.reply_to_message_with_keyboard(message, send_message, get_json_localization("subscribe_inform_button"),
                                            get_json_localization("unsubscribe_inform_button"),
                                            get_json_localization("subscribes_button"),
                                            get_json_localization("user_subscribes_button"),
                                            get_json_localization("unsubscribe_button"),
                                            get_json_localization("unsubscribe_all_button"),
                                            get_json_localization("back_button"))
        self.show_user_subscriptions(message)
        self.change_state(self.state_message_settings)
        return source, topic

    def state_unsubscribe_prepare(self, message):
        user_message = message.text.strip()
        if user_message in lists.back:
            self.reply_to_message_with_keyboard(message, get_json_localization("messages"),
                                                get_json_localization("subscribe_inform_button"),
                                                get_json_localization("unsubscribe_inform_button"),
                                                get_json_localization("subscribes_button"),
                                                get_json_localization("user_subscribes_button"),
                                                get_json_localization("unsubscribe_button"),
                                                get_json_localization("unsubscribe_all_button"),
                                                get_json_localization("back_button"))
            self.change_state(self.state_message_settings)
            return
        elif user_message == get_json_localization("confirm_button"):
            self.unsubscribe_all(message)

    def unsubscribe_all(self, message):
        """ unsubscribe from all subscriptions """
        telegram_id = get_telegram_id(message)
        self.config.delete_all_subscriptions(telegram_id)
        send_message = get_json_localization("unsubscribe_from_all_subscriptions")
        logger.info(
            get_json_localization("unsubscribe_from_all") + f', user_id: {telegram_id},'
                                                            f' subscribe -> message_settings')
        self.reply_to_message_with_keyboard(message, send_message,
                                            get_json_localization("subscribe_inform_button"),
                                            get_json_localization("unsubscribe_inform_button"),
                                            get_json_localization("subscribes_button"),
                                            get_json_localization("user_subscribes_button"),
                                            get_json_localization("unsubscribe_button"),
                                            get_json_localization("unsubscribe_all_button"),
                                            get_json_localization("back_button"))
        self.show_user_subscriptions(message)
        self.change_state(self.state_message_settings)
        return

    def state_prepare_to_delete_time(self, message):
        telegram_id = get_telegram_id(message)
        user_message = message.text.strip()
        ability_to_send_messages = self.config.get_ability_to_send_messages(telegram_id)

        if user_message == get_json_localization("confirm_button"):
            self.state_delete_time(message)
            if not ability_to_send_messages:
                send_message = get_json_localization(
                    "removing_the_time_limit_for_sending_a_message") + get_json_localization(
                    "hint_for_receiving messages")
            else:
                send_message = get_json_localization("removing_the_time_limit_for_sending_a_message")
            logger.info(get_json_localization("clear_the_time_limit_for_sending_a_message") + f'user_id: {telegram_id}')
            self.send_message_with_keyboard(message.chat.id,
                                            send_message,
                                            get_json_localization("set_time_button"),
                                            get_json_localization("delete_time_button"),
                                            get_json_localization("show_settings_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_settings_choose)

        elif user_message in lists.back:
            self.send_message_with_keyboard(message.chat.id, get_json_localization("settings"),
                                            get_json_localization("set_time_button"),
                                            get_json_localization("delete_time_button"),
                                            get_json_localization("show_settings_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_settings_choose)

    def state_delete_time(self, message):
        telegram_id = get_telegram_id(message)
        self.config.delete_user_sending_time_period(telegram_id, )
        return

    def state_get_user_time_period(self, message: types.Message):
        """ get user time_from and time_to configuration to send_messages"""
        telegram_id = get_telegram_id(message)
        user_message = message.text.strip()
        user_text = message.text
        if user_message in lists.back:
            self.send_message_with_keyboard(message.chat.id, get_json_localization("settings"),
                                            get_json_localization("set_time_button"),
                                            get_json_localization("delete_time_button"),
                                            get_json_localization("show_settings_button"),
                                            get_json_localization("back_button"))
            self.change_state(self.state_settings_choose)
            return
        try:
            start_hour, end_hour = parse_time_period(user_text)
        except WrongHour:
            error_message3 = get_json_localization("incorrect_time_value_error")
            self.bot.reply_to(message, error_message3, parse_mode='html')
            logging.error(
                f'bot_send_message: {get_json_localization("incorrect_time_value")} user_id: {telegram_id}')
            send_param3 = get_json_localization("enter_the_time_to_send_messages")
            time.sleep(1)
            self.send_message(message.chat.id, send_param3)
            logger.debug(
                f'bot_send_message: {get_json_localization("enter_the_time_to_send_messages")}, user_id: {telegram_id}')
            return
        except Exception:
            error_message = get_json_localization("enter_incorrect_error")
            self.bot.reply_to(message, error_message, parse_mode='html')
            logging.error(
                f'bot_send_message: {get_json_localization("enter_incorrect_error")}, user_id: {telegram_id}')
            send_message = get_json_localization("enter_the_time_to_send_messages")
            time.sleep(1)
            self.send_message(message.chat.id, send_message)
            logger.debug(
                f'bot_send_message: {get_json_localization("enter_the_time_to_send_messages")}, user_id: {telegram_id}')
            return

        self.config.set_user_data(telegram_id, start_hour, end_hour)
        ability_to_send_messages = self.config.get_ability_to_send_messages(telegram_id)
        if not ability_to_send_messages:
            send_message = get_json_localization("user_set_value") + get_json_localization("from") + \
                           str(start_hour) + get_json_localization("on") + str(end_hour) + '.' + \
                           get_json_localization("hours") + get_json_localization("hint_for_receiving messages")
        else:
            send_message = get_json_localization("user_set_value") + get_json_localization("from") + str(
                start_hour) + get_json_localization("on") + str(
                end_hour) + get_json_localization("hours")

        self.bot.reply_to(message, send_message, reply_markup=types.ReplyKeyboardRemove(), parse_mode='html')

        self.send_message_with_keyboard(message.chat.id, get_json_localization("menu"),
                                        get_json_localization("message_button"),
                                        get_json_localization("settings_button"))
        self.change_state(self.state_settings)
