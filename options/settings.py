import logging
import dotenv
import os

environ = os.environ
DATA_DIR = environ.get("DATA_DIR", "data")
DEFAULT_DOTENV_PATH = os.path.join(DATA_DIR, '.env')
dotenv_path = environ.get('DOTENV_PATH', DEFAULT_DOTENV_PATH)
print(f"Reading env from {os.path.abspath(dotenv_path)}", flush=True)
dotenv.load_dotenv(dotenv_path)

DEBUG_FILE_PATH = environ.get('DEBUG_FILE_PATH', os.path.join(DATA_DIR, 'debug.log'))
INFO_FILE_PATH = environ.get('INFO_FILE_PATH', os.path.join(DATA_DIR, 'info.log'))

TOKEN_URL = environ["TOKEN_URL"]
API_TOKEN = environ["API_TOKEN"]
LANGUAGE = environ["LANGUAGE"]

DATABASE_HOST = environ["DATABASE_HOST"]
DATABASE_USER = environ["DATABASE_USER"]
DATABASE_PASSWD = environ["DATABASE_PASSWD"]
DATABASE_PORT = int(environ["DATABASE_PORT"])
DATABASE = environ["DATABASE"]

SSL_CERTIFICATE_PATH = environ["SSL_CERTIFICATE_PATH"]
SSL_KEY_PATH = environ["SSL_KEY_PATH"]

SERVER_PORT = int(environ["SERVER_PORT"])
PASSWORD = environ["PASSWORD"]
COUNT_AUTH = int(environ["COUNT_AUTH"])

LOGGING_LEVEL = logging.DEBUG if environ["LOGGING_LEVEL"] == 'DEBUG' \
    else logging.INFO if environ["LOGGING_LEVEL"] == 'INFO' \
    else None

WAIT_TIME_TO_MISSED_MESSAGES = float(environ["WAIT_TIME_TO_MISSED_MESSAGES"])
WAIT_AFTER_EXCEPTION = float(environ["WAIT_AFTER_EXCEPTION"])
FIRST_MISSED_MESSAGES = int(environ["FIRST_MISSED_MESSAGES"])
LAST_MISSED_MESSAGES = int(environ["LAST_MISSED_MESSAGES"])
LENGTH_SOURCE = int(environ["LENGTH_SOURCE"])
LENGTH_TOPIC = int(environ["LENGTH_TOPIC"])
LENGTH_SOURCE_TOPIC = int(environ["LENGTH_SOURCE_TOPIC"])
LENGTH_MESSAGE = int(environ["LENGTH_MESSAGE"])
