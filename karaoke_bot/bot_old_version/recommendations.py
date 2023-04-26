from datetime import datetime


class Recommendation:

    def __init__(self, user_id: int, url: str, time: datetime, rec_type: str, is_accepted=False):
        self.user_id = user_id
        self.url = url
        self.time = time
        self.rec_type = rec_type
        self.is_accepted = is_accepted
