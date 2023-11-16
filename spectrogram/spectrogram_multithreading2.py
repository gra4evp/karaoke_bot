import librosa
import matplotlib.pyplot as plt
import numpy as np
import os
import time
import threading


def get_audio_sample(audio, sr, start, duration):
    return audio[start * sr:(start + duration) * sr]


def get_spectrogram_pair(
        audio,
        sr,
        start: int,
        duration: int,
        overlap: int,
        volume: int = 1,
        frame_size: int = 2048,
        hop_size: int = 512
):

    sample1 = get_audio_sample(audio, sr, start=start, duration=duration) * volume
    sample2 = get_audio_sample(audio, sr, start=start + duration - overlap, duration=duration) * volume

    spec1 = librosa.stft(sample1, n_fft=frame_size, hop_length=hop_size)
    spec2 = librosa.stft(sample2, n_fft=frame_size, hop_length=hop_size)

    return spec1, spec2


def process_files(filenames, folder_path, pairs, lock):
    while filenames:
        with lock:
            filename = filenames.pop(0)  # Извлекаем первый файл из списка

        y, sr = librosa.load(os.path.join(folder_path, filename), sr=44100, mono=True)
        for i in range(pairs):
            start = 30 + i * 5
            sp1, sp2 = get_spectrogram_pair(audio=y, sr=sr, start=start, duration=20, overlap=5)


if __name__ == '__main__':
    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)
    number_sample_pairs = 8
    workers = 4  # Задайте желаемое количество потоков

    start_time = time.time()
    lock = threading.Lock()  # Создаем мьютекс

    threads = []
    for _ in range(workers):
        thread = threading.Thread(target=process_files, args=(filenames, folder_path, number_sample_pairs, lock))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    execution_time = time.time() - start_time
    print(f"Processing completed in {execution_time} seconds")
