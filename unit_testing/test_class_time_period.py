import datetime
import unittest
from bot_config.timeperiod import TimePeriod


class TestTimePeriod(unittest.TestCase):
    def test_1(self):
        time_from = 7
        time_to = 10
        time_period = TimePeriod(time_from, time_to)
        dt = datetime.datetime(2021, 6, 15, 6, 21, 14)
        assert not time_period.is_time_inside(dt)

    def test_2(self):
        time_from = 7
        time_to = 10
        time_period = TimePeriod(time_from, time_to)
        dt = datetime.datetime(2021, 6, 15, 9, 21, 15)
        assert time_period.is_time_inside(dt)

    def test_3(self):
        time_from = 14
        time_to = 13
        time_period = TimePeriod(time_from, time_to)
        dt = datetime.datetime(2021, 6, 15, 0, 21, 15)
        assert time_period.is_time_inside(dt)


def main():
    TestTimePeriod()


if __name__ == "__main__":
    unittest.main()
