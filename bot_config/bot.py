import time
# noinspection PyPackageRequirements
import telebot
# noinspection PyPackageRequirements
from telebot import types
import logging
from bot_config.db_config import Config
from db.data_base import Database1
from bot_config.fsm import FSM
import threading
from localize.json_translate import get_json_localization
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, api_token, bot_password, count_auth, host, user, db_password, port, database, set_wait_time,
                 len_s, len_t, len_s_t, len_m):
        self.api_token = api_token
        self.bot_password = bot_password
        self.count_auth = count_auth
        self.bot = telebot.TeleBot(self.api_token, threaded=True)
        self.db_host = host
        self.db_user = user
        self.db_password = db_password
        self.db_port = port
        self.database = database
        self.set_wait_time = set_wait_time
        self.db = Database1(host=self.db_host, user=self.db_user, passwd=self.db_password, port=self.db_port,
                            database=self.database, len_s=len_s, len_t=len_t, len_m=len_m, len_s_t=len_s_t)
        self.config = Config(self.db)
        self.current_fsm_dict = dict()
        self.current_fsm_dict_lock = threading.RLock()

        @self.bot.message_handler(commands=['start'])
        def call_authorized(message):
            logger.info(get_json_localization("bot_has_launched"))
            telegram_id = message.chat.id
            is_block = self.config.get_block_users(telegram_id)
            if is_block == 1:
                pass
            else:
                db_pass = self.config.get_password(telegram_id)
                if db_pass == 1:
                    self.authorized_without_password(message)
                else:
                    self.authorized(message)

        @self.bot.message_handler(content_types=['text'])
        def call_process_message(message):
            self.process_message(message)

    def send_message(self, chat_id, message, *buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for button in buttons:
            type_button = types.KeyboardButton(button)
            markup.add(type_button)
        self.bot.send_message(chat_id, message, reply_markup=markup, parse_mode='html')

    def reply_to_message(self, message, send_message, *buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        for button in buttons:
            type_button = types.KeyboardButton(button)
            markup.add(type_button)
        self.bot.reply_to(message, send_message, reply_markup=markup, parse_mode='html')

    def authorized_without_password(self, message):
        telegram_id = message.chat.id
        logger.debug('start_the_bot')
        self.send_message(message.chat.id, get_json_localization("main_menu"), get_json_localization("message_button"),
                          get_json_localization("settings_button"))
        logger.debug(f'bot_send_message: {get_json_localization("main_menu")}, user_id: {telegram_id},'
                     f' greetings -> state_settings ')
        with self.current_fsm_dict_lock:
            self.current_fsm_dict[telegram_id] = FSM(self.bot, self.process_message, self.config, self.bot_password,
                                                     self.count_auth)
            self.current_fsm_dict[telegram_id].start_without_password()

    def authorized(self, message):
        telegram_id = message.chat.id
        logger.debug('start the bot, request password')
        self.bot.send_message(telegram_id, get_json_localization("first_launch"), parse_mode='html')
        with self.current_fsm_dict_lock:
            self.current_fsm_dict[telegram_id] = FSM(self.bot, self.process_message, self.config, self.bot_password,
                                                     self.count_auth)
            self.current_fsm_dict[telegram_id].start()

    def greetings(self, message):
        telegram_id = message.chat.id
        logger.debug(f'Function - greetings, user_id: {telegram_id}')
        self.reply_to_message(message, get_json_localization("main_menu"), get_json_localization("message_button"),
                              get_json_localization("settings_button"))
        self.bot.register_next_step_handler(message, self.process_message)

    def get_telegram_id(self):
        while True:
            telegram_id = self.config.get_telegram_id()
            while telegram_id:
                time.sleep(self.set_wait_time)
                return telegram_id

    def run_fsm(self, message):
        telegram_id = message.chat.id
        with self.current_fsm_dict_lock:
            if self.current_fsm_dict.get(telegram_id) is not None:
                self.current_fsm_dict[telegram_id].run(message)
                if self.current_fsm_dict[telegram_id].is_finished():
                    self.current_fsm_dict[telegram_id] = None

    def get_telegram_bot(self):
        return self.bot

    def get_config(self):
        return self.config

    def process_message(self, message):
        telegram_id = message.chat.id
        with self.current_fsm_dict_lock:
            if self.current_fsm_dict.get(telegram_id) is not None:
                self.run_fsm(message)

    def polling(self, wait_after_except):
        try:
            self.bot.infinity_polling()
        except KeyboardInterrupt:
            logger.info(get_json_localization("polling_stop_keyboard_interrupt"))
            return
        except Exception as e:
            logger.error(f'Polling exception: {type(e).__name__} ', exc_info=True)
            time.sleep(wait_after_except)
