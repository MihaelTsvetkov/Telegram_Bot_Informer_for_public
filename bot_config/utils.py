class WrongHour(RuntimeError):
    pass


class WrongValue(RuntimeError):
    pass


true_element = ['Минута', 'минут', 'минута', 'Минут', 'Минуту', 'минуту', 'Minute', 'minute', 'Час', 'Hour', 'час',
                'hour', 'day', 'Day', 'День', 'день', 'mounth', 'Mounth', 'Месяц', 'месяц', 'year', 'Year', 'Год',
                'год']


def parse_time_period(period: str):
    """ a-b """
    values = period.split('-')
    is_error = len(values) != 2
    if is_error:
        raise RuntimeError(f"Неверный формат в функции parse_period: '{period}'")
    time_from = int(values[0])  # ValueError
    time_to = int(values[1])
    wrong_time_from = time_from >= 24
    wrong_time_to = time_to >= 24
    if wrong_time_from:
        raise WrongHour(f"Некоректное значение времени: '{period}'")
    if wrong_time_to:
        raise WrongHour(f"Некоректное значение времени: '{period}'")
    return time_from, time_to


def parse_subscribe(period: str):
    values = period.split('/')
    if len(values) == 2:
        source = values[0]
        topic = values[1]
        return source, topic
    else:
        source = values[0]
        topic = None
        return source, topic
