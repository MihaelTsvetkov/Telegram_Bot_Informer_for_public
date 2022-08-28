from db.convert import convert_list_for_int_and_float
import mysql
import mysql.connector


class Database1:
    def __init__(self, host, user, passwd, port, database, len_s, len_t, len_m, len_s_t):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.send_info_table = "send_info"
        self.available_subscribes_table = 'available_subscribes'
        self.user_sub_table = 'user_subscribes'
        self.missed_mes_table = 'missed_messages'
        self.port = port
        self.database = database
        self.len_s = len_s
        self.len_t = len_t
        self.len_s_t = len_s_t
        self.len_m = len_m
        self.create_tables()

    def _get_connection(self):
        return mysql.connector.connect(host=self.host, user=self.user, passwd=self.passwd, database=self.database)

    def find_telegram_id(self, telegram_id, connection):
        with connection.cursor() as cursor:
            query = f"""SELECT telegram_id
            FROM {self.send_info_table} WHERE telegram_id = {telegram_id}"""
            cursor.execute(query)
            return cursor.fetchall()

    def create_tables(self):
        self.create_table_send_info()
        self.create_table_available_subscribes()
        self.create_table_user_subscribes()
        self.create_table_missed_messages()

    def set_user_data(self, telegram_id, time_from, time_to):
        with self._get_connection() as connection:
            is_telegram_id_present = bool(self.find_telegram_id(telegram_id, connection))
            if is_telegram_id_present:
                sql = f'UPDATE {self.send_info_table} set time_from = %s, time_to = %s WHERE telegram_id = %s '
                val = (time_from, time_to, telegram_id)
            else:
                sql = f"INSERT INTO {self.send_info_table}(input_password, telegram_id, time_from, time_to) " \
                      f"VALUES (%s, %s, %s, %s)"
                val = (telegram_id, time_from, time_to)
            with connection.cursor() as cursor:
                cursor.execute(sql, val)
                connection.commit()

    # def set_send_configuration(self, telegram_id, number_msg, per_time):
    #     with self._get_connection() as connection:
    #         is_telegram_id_present = bool(self.find_telegram_id(telegram_id, connection))
    #         if is_telegram_id_present:
    #             sql = f'UPDATE {self.send_info_table} set number_msg = %s, per_time = %s WHERE telegram_id = %s '
    #             val = (number_msg, per_time, telegram_id)
    #         else:
    #             sql = f"INSERT INTO {self.send_info_table} (input_password, telegram_id, number_msg, per_time) " \
    #                   f"VALUES (%s, %s, %s, %s)"
    #             val = (telegram_id, number_msg, per_time)
    #         with connection.cursor() as cursor:
    #             cursor.execute(sql, val)
    #             connection.commit()

    def create_database(self):
        with self._get_connection() as connection:
            with connection.cursor as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
                connection.commit()

    def create_table_send_info(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.send_info_table}(block TINYINT, "
                               f"input_password TINYINT, "
                               f"telegram_id BIGINT, time_from INT, "
                               f"time_to INT, counter BIGINT, "
                               "ability_to_send TINYINT, "
                               "last_msg_dt TIMESTAMP NULL, username VARCHAR(100), chat_name VARCHAR(100) )")
                connection.commit()

    def create_table_available_subscribes(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.available_subscribes_table}"
                               f"(source VARCHAR({self.len_s}), topic VARCHAR({self.len_t}))")
                connection.commit()

    def create_table_user_subscribes(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.user_sub_table}(telegram_id BIGINT, "
                               f"user_source VARCHAR({self.len_s}), "
                               f"user_topic VARCHAR({self.len_t}))")
                connection.commit()

    def create_table_missed_messages(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.missed_mes_table}(telegram_id BIGINT, "
                               f"source_topic_time VARCHAR({self.len_s_t}), message VARCHAR({self.len_m}), "
                               f"message_time TIMESTAMP NULL)")
                connection.commit()

    def set_user_topic(self, user_topic):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql_check = f"""SELECT telegram_id, user_topic FROM {self.user_sub_table}"""
                if sql_check == user_topic:
                    pass
                else:
                    sql = "INSERT INTO user_subscribes(User_topic)"
                    val = (user_topic,)
                    cursor.execute(sql, val)
                    connection.commit()

    def set_user_source(self, user_source):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql_check = f"""SELECT user_topic FROM {self.user_sub_table}"""
                if sql_check == user_source:
                    pass
                else:
                    sql = f"INSERT INTO {self.user_sub_table} User_source = %s"
                    val = (user_source,)
                    cursor.execute(sql, val)
                    connection.commit()

    def get_user_config(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT telegram_id, ability_to_send FROM {self.send_info_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                return result

    def get_sources_and_topics(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT source, topic FROM {self.available_subscribes_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                source_topic = dict()
                for row in result:
                    source, topic = row
                    source_topic.setdefault(source, []).append(topic)
                return source_topic

    def get_sources_and_topics_for_check(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT source, topic FROM {self.available_subscribes_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_user_sources_and_topics_for_check(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_source, user_topic FROM {self.user_sub_table} WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_sources(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT source FROM {self.available_subscribes_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def set_user_name(self, telegram_id, username):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                db_telegram_id = f'SELECT telegram_id FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(db_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    sql = f'INSERT INTO {self.send_info_table}(telegram_id, username) VALUES(%s, %s)'
                    val = (telegram_id, username)
                    cursor.execute(sql, val)
                    connection.commit()
                else:
                    sql = f'UPDATE {self.send_info_table} SET username = %s WHERE telegram_id = %s'
                    val = (username, telegram_id)
                    cursor.execute(sql, val)
                    connection.commit()

    def get_user_name(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT username FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    result = []
                    return result
                else:
                    clear_result = result[0]
                    final_result = clear_result[0]
                    return final_result

    def set_chat_name(self, telegram_id, chatname):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT telegram_id FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    sql = f'INSERT INTO {self.send_info_table}(telegram_id, chat_name) VALUES(%s, %s)'
                    val = (telegram_id, chatname)
                    cursor.execute(sql, val)
                    connection.commit()
                else:
                    sql = f'UPDATE {self.send_info_table} SET chat_name = %s WHERE telegram_id = %s'
                    val = (chatname, telegram_id)
                    cursor.execute(sql, val)

    def get_chat_name(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT chat_name FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    result = []
                    return result
                else:
                    clear_result = result[0]
                    final_result = clear_result[0]
                    return final_result

    def get_topics(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT topic FROM {self.available_subscribes_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_user_topics(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_topic FROM {self.user_sub_table} WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_user_sources(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_source FROM {self.user_sub_table} WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_user_sources_and_topics(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_source, user_topic FROM {self.user_sub_table} 
                WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    source_topic = dict()
                    for row in result:
                        source, topic = row
                        source_topic.setdefault(source, []).append(topic)
                    return source_topic
                else:
                    result = []
                    return result

    def set_password(self, telegram_id, pass_check):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT telegram_id FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    sql = f'INSERT INTO {self.send_info_table}(telegram_id, input_password) VALUES(%s, %s)'
                    val = (telegram_id, pass_check)
                    cursor.execute(sql, val)
                    connection.commit()
                else:
                    sql = f'UPDATE {self.send_info_table} SET input_password = %s WHERE telegram_id = %s'
                    val = (pass_check, telegram_id)
                    cursor.execute(sql, val)
                    connection.commit()

    def get_password(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = f'SELECT input_password FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(sql, val)
                result = cursor.fetchall()
                if result:
                    clear_result = result[0]
                    final_result = clear_result[0]
                    return final_result
                else:
                    result = []
                    return result

    def get_user_topics_sources(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_source, user_topic FROM {self.user_sub_table}
                  WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def set_user_topic_and_source(self, source, topic, telegram_id):
        subscription = (source, topic)
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT user_source, user_topic from {self.user_sub_table} 
                WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if subscription in result:
                    pass
                else:
                    sql = f"""INSERT INTO {self.user_sub_table} (telegram_id, user_source, user_topic)  
                                               VALUES (%s, %s, %s)"""
                    val = (telegram_id, source, topic,)
                    cursor.execute(sql, val)
                    connection.commit()

    def set_missed_message_time_period(self, source_topic_time, message, telegram_id, time):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = f'INSERT INTO {self.missed_mes_table}(telegram_id, source_topic_time, message, ' \
                      f'message_time) '\
                      f'VALUES(%s, %s, %s, %s)'
                val = (telegram_id, source_topic_time, message, time)
                cursor.execute(sql, val)
                connection.commit()

    def get_missed_sources_and_topics_and_messages(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT source_topic_time, message, message_time FROM {self.missed_mes_table} 
                WHERE telegram_id = %s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return result
                else:
                    result = []
                    return result

    def get_missed_messages_counter(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT telegram_id FROM {self.missed_mes_table} WHERE telegram_id = %s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    return len(result)
                else:
                    return 0

    def delete_user_topic_and_source(self, source, topic, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""DELETE FROM {self.user_sub_table} WHERE telegram_id = %s AND 
                user_source = %s AND user_topic = %s """
                val = (telegram_id, source, topic)
                cursor.execute(query, val)
                connection.commit()

    def delete_all_subscriptions(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""DELETE FROM {self.user_sub_table} WHERE telegram_id = %s """
                val = (telegram_id,)
                cursor.execute(query, val)
                connection.commit()

    def delete_user_sending_time_period(self, telegram_id, ):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""UPDATE {self.send_info_table} SET time_from = null, time_to = null WHERE telegram_id = %s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                connection.commit()

    def clear_missed_message(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""DELETE FROM {self.missed_mes_table} WHERE telegram_id = %s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                connection.commit()

    def get_time_period(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT  time_from, time_to FROM {self.send_info_table} WHERE telegram_id = %s"""
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    final_result = result[0]
                else:
                    final_result = []
                return final_result

    def set_ability_to_send_message(self, telegram_id, ability_to_send):
        with self._get_connection() as connection:
            is_telegram_id_present = bool(self.find_telegram_id(telegram_id, connection))
            if is_telegram_id_present:
                sql = f'UPDATE {self.send_info_table} SET ability_to_send = %s WHERE telegram_id = %s'
                val = (ability_to_send, telegram_id)
            else:
                sql = f"""INSERT INTO {self.send_info_table}(telegram_id, ability_to_send) VALUES (%s, %s)"""
                val = (telegram_id, ability_to_send)
            with connection.cursor() as cursor:
                cursor.execute(sql, val)
                connection.commit()

    def clear_ability_to_send_message(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                is_telegram_id_present = bool(self.find_telegram_id(telegram_id, connection))
                if is_telegram_id_present:
                    sql = f'UPDATE {self.send_info_table} SET ability_to_send = null WHERE telegram_id = %s'
                    val = (telegram_id,)
                    cursor.execute(sql, val)
                    connection.commit()

    def get_ability_to_send_messages(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT ability_to_send FROM {self.send_info_table} WHERE telegram_id =%s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                result = cursor.fetchall()
                if result:
                    clear_result = result[0]
                    for items in clear_result:
                        if items is not None:
                            return True
                else:
                    return False

    def get_telegram_id(self):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT telegram_id FROM {self.send_info_table}"""
                cursor.execute(query)
                result = cursor.fetchall()
                clear_result = convert_list_for_int_and_float(result)
                return clear_result

    def get_message_counter(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT counter FROM {self.send_info_table} WHERE telegram_id = %s"""
                val = (telegram_id,)
                cursor.execute(query, val)
                result = cursor.fetchone()
                clear_result = result[0]
                return clear_result

    def set_message_counter(self, counter, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = f'UPDATE {self.send_info_table} set counter = %s WHERE telegram_id = %s'
                val = (counter, telegram_id)
                cursor.execute(sql, val)
                connection.commit()

    def get_last_msg_dt(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""SELECT last_msg_dt FROM {self.send_info_table} WHERE telegram_id = %s """
                val = (telegram_id, )
                cursor.execute(query, val)
                result = cursor.fetchone()
                clear_result = result[0]
                return clear_result

    def set_last_msg_dt(self, last_msg_dt, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                sql = f'UPDATE {self.send_info_table} set last_msg_dt = %s WHERE telegram_id = %s'
                val = (last_msg_dt, telegram_id)
                cursor.execute(sql, val)
                connection.commit()

    def add_block_users(self, telegram_id, block):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT telegram_id FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    sql = f'INSERT INTO {self.send_info_table}(telegram_id, block) VALUES(%s, %s)'
                    val = (telegram_id, block)
                    cursor.execute(sql, val)
                    connection.commit()
                else:
                    sql = f'UPDATE {self.send_info_table} SET block = %s WHERE telegram_id = %s'
                    val = (block, telegram_id)
                    cursor.execute(sql, val)
                    connection.commit()

    def get_block_users(self, telegram_id):
        with self._get_connection() as connection:
            with connection.cursor() as cursor:
                get_telegram_id = f'SELECT block FROM {self.send_info_table} WHERE telegram_id = %s'
                val = (telegram_id,)
                cursor.execute(get_telegram_id, val)
                result = cursor.fetchall()
                if not result:
                    result = []
                    return result
                else:
                    clear_result = result[0]
                    final_result = clear_result[0]
                    return final_result
