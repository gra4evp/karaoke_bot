from typing import Dict
from yt_dlp import YoutubeDL


class YouTubeVideo:

    def __init__(self, url: str):
        self.url: str = url
        self.video_info: Dict[str, str] = {}

    def get_info(self) -> Dict[str, str]:
        if not self.video_info:
            ydl_opts = {'quiet': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.video_info = {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', ''),
                    'uploader': info.get('uploader', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'categories': info.get('categories', [])
                }
        return self.video_info

    def __str__(self) -> str:
        return f"YouTubeVideo: title - {self.video_info['title']} id - {self.video_info['video_id']}"

    def __repr__(self) -> str:
        return f"YouTubeVideo(url='{self.url}')"


if __name__ == '__main__':
    track_url = input("Введите URL видео на YouTube: ")
    video = YouTubeVideo(track_url)

    for key, value in video.get_info().items():
        print(f"{key}: {value}")

    # info = ydl.extract_info(url, download=False)
    # print(json.dumps(ydl.sanitize_info(info), indent=2))