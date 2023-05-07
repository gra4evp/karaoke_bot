from datetime import datetime
import random
from karaoke_bot.bot_old_version.unique_links_parse import load_links_by_user_id, get_unique_links

unique_links = get_unique_links('id_url_all.csv')
links_by_user_id = load_links_by_user_id('links_by_user_id.json')


class Recommendation:

    def __init__(self,
                 message_id: int,
                 user_id: int,
                 dt: datetime,
                 rec_type: str | None = None,
                 is_accepted: bool = False):
        self.message_id = message_id
        self.user_id = user_id
        self.dt = dt
        self.rec_type = rec_type
        self.is_accepted = is_accepted

    def get_recommendation(self) -> str:
        links = links_by_user_id.get(str(self.user_id))
        if links:
            link = links.pop(random.randint(0, len(links) - 1))
        else:
            link = random.choice(list(unique_links))
        return link


recommendations: list[Recommendation] = []
