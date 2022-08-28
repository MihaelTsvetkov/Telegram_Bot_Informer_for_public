class TimePeriod:
    def __init__(self, from_hour, to_hour):
        self.from_hour = from_hour
        self.to_hour = to_hour

    def set_period(self, from_hour, to_hour):
        self.from_hour = from_hour
        self.to_hour = to_hour

    def is_time_inside(self, dt) -> bool:
        if self.from_hour is None and self.to_hour is None:
            return True
        if self.from_hour <= self.to_hour:
            return self.from_hour <= dt.hour < self.to_hour
        else:
            if self.from_hour <= dt.hour:
                return True
            else:
                return dt.hour < self.to_hour
