class CheckSub:
    def __init__(self, user_topics_sources: tuple, inform_check: bool):
        self.user_topics_sources = user_topics_sources
        self.inform_check = inform_check

    def check_the_values(self, topic, source):
        subscription = (source, topic)
        all_topics = '*'
        extended_subscription = (source, all_topics)

        if subscription in self.user_topics_sources and self.inform_check == 1:
            return True
        elif extended_subscription in self.user_topics_sources and self.inform_check == 1:
            return True
        else:
            return False
