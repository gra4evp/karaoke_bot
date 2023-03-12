from typing import Dict
from yt_dlp import YoutubeDL


def get_video_info(url: str) -> Dict[str, str]:
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': './%(title)s.%(ext)s',
        'cachedir': './',
        'noplaylist': True,
        'extractaudio': True,
    }
    with YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        video_info = {
            'title': info.get('title', ''),
            'uploader': info.get('uploader', ''),
            'description': info.get('description', ''),
            'duration': info.get('duration', 0),
            'view_count': info.get('view_count', 0),
            'like_count': info.get('like_count', 0),
            'dislike_count': info.get('dislike_count', 0),
            'comment_count': info.get('comment_count', 0),
            'categories': info.get('categories', []),
            'video_id': info.get('id', '')
        }
    return video_info


if __name__ == '__main__':
    url = input("Введите URL видео на YouTube: ")
    info = get_video_info(url)

    print("Title:", info["title"])
    print("Uploader:", info["uploader"])
    print("Description:", info["description"])
    print("Duration:", info["duration"], "seconds")
    print("View count:", info["view_count"])
    print("Likes:", info["like_count"])
    print("Dislikes:", info["dislike_count"])
    print("Comments:", info["comment_count"])
    print("Categories:", info["categories"])
    print("Video ID:", info["video_id"])