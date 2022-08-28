import unittest
from bot_config.authorized import Authorized


class WrongPasswordError:
    pass


class TestAuthorized(unittest.TestCase):
    def test_with_false_password(self):
        password = 12345
        authorized = Authorized(true_password=1234)
        assert not authorized.check_password(password)

    def test_with_true_password(self):
        password = 1234
        authorized = Authorized(true_password=1234)
        assert authorized.check_password(password)


def main():
    TestAuthorized()


if __name__ == "__main__":
    unittest.main()
