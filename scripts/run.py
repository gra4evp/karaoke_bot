import subprocess
import argparse
from music2vec.extraction import Extractor
from yt_dlp import YoutubeDL
import ffmpeg
import json


def download_video_youtube(url: str):
    url = url.replace('&', '"&"')
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
    with YoutubeDL(ydl_opts) as ydl:
        error_code = ydl.download(url)
        info = ydl.extract_info(url, download=False)
        print(info['id'], info['description'])
        # print(json.dumps(ydl.sanitize_info(info), indent=2))


def wav2vec(file_wav):
    extractor = Extractor()
    genres, features = extractor(file_wav)
    print(*genres)
    print(*features)


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        title='subcommands',
        description="All subcommands",
        help="When typing a subcommand, the corresponding function of the same name will be called.",
        dest='subparser_name')

    parser_download = subparsers.add_parser('dwld')
    parser_download.add_argument('link', type=str)

    parser_music2vec = subparsers.add_parser('m2v')
    parser_music2vec.add_argument('filepath', type=str)

    parser_convert = subparsers.add_parser('convert')
    parser_convert.add_argument('link')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    if args.subparser_name == 'dwld':
        download_video_youtube(url=args.link)

    if args.subparser_name == 'm2v':
        wav2vec(file_wav=args.filepath)
