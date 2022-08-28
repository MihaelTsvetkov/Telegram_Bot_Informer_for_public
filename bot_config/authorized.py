class Authorized:
    def __init__(self, true_password):
        self.true_password = true_password

    def check_password(self, password):
        return password == self.true_password

