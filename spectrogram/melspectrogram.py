import librosa
import matplotlib.pyplot as plt
import numpy as np
import os
import time


def get_audio_sample(audio, sr, start, duration):
    return audio[start * sr:(start + duration) * sr]


def get_spectrogram_pair_v1(folder_path, filenames, volume=1, frame_size=2048, hop_size=512, srate=44100):
    y, sr = librosa.load(os.path.join(folder_path, filenames[0]), sr=srate, mono=True)

    start = 40
    duration = 25  # Длина сегмента в секундах
    overlap = 5  # Длина перекрытия в секундах

    sample1 = get_audio_sample(y, sr, start=start, duration=duration) * volume
    sample2 = get_audio_sample(y, sr, start=start + duration - overlap, duration=duration) * volume

    spec1 = librosa.stft(sample1, n_fft=frame_size, hop_length=hop_size)
    spec2 = librosa.stft(sample2, n_fft=frame_size, hop_length=hop_size)

    return spec1, spec2


def get_spectrogram_pair_v2(folder_path, filenames, volume=1, frame_size=2048, hop_size=512, srate=44100):
    y, sr = librosa.load(os.path.join(folder_path, filenames[0]), sr=srate, mono=True)

    start = 40
    duration = 25  # Длина сегмента в секундах
    overlap = 5  # Длина перекрытия в секундах

    sample = y[start * sr:(start + 2*duration - overlap) * sr] * volume

    spec = librosa.stft(sample, n_fft=frame_size, hop_length=hop_size)
    spec = spec[:, :len(spec[0]) - len(spec[0]) % 2]  # Делаем четное количество временных кадров

    spec1 = spec[:, :len(spec[0]) // 2]
    spec2 = spec[:, len(spec[0]) // 2:]
    return spec1, spec2


def plot_4(spec1v1, spec1v2, spec2v1, spec2v2, sample_rate):
    plt.subplot(2, 2, 1)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec1v1), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample1 V1')

    plt.subplot(2, 2, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec1v2), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample2 V1')

    plt.subplot(2, 2, 3)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v1), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample1 V2')

    plt.subplot(2, 2, 4)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v2), ref=np.max), sr=sample_rate, y_axis='log',
                             x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample2 V2')

    plt.tight_layout()
    plt.show()


def plot_4volume(spec1v1, spec1v2, spec2v1, spec2v2, sample_rate, volume=2):
    plt.subplot(2, 2, 1)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec1v1), ref=np.max), sr=sample_rate, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample1')

    plt.subplot(2, 2, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec1v2), ref=np.max), sr=sample_rate, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('sample2')

    plt.subplot(2, 2, 3)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v1), ref=np.max), sr=sample_rate, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'sample1 * {volume}')

    plt.subplot(2, 2, 4)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spec2v2), ref=np.max), sr=sample_rate, y_axis='log', x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title(f'sample2 * {volume}')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)
    sample_rate = 44100

    # spec1v1, spec1v2 = get_spectrogram_pair_v1(folder_path=folder_path, filenames=filenames, srate=sample_rate)
    # spec2v1, spec2v2 = get_spectrogram_pair_v2(folder_path=folder_path, filenames=filenames, srate=sample_rate)
    # plot_4(spec1v1=spec1v1, spec1v2=spec1v2, spec2v1=spec2v1, spec2v2=spec2v2, sample_rate=sample_rate)

    # volume = 5
    # spec1v1, spec1v2 = get_spectrogram_pair_v1(folder_path=folder_path, filenames=filenames, volume=1, srate=sample_rate)
    # spec2v1, spec2v2 = get_spectrogram_pair_v1(folder_path=folder_path, filenames=filenames, volume=volume, srate=sample_rate)
    # plot_4volume(spec1v1=spec1v1, spec1v2=spec1v2, spec2v1=spec2v1, spec2v2=spec2v2, sample_rate=sample_rate, volume=volume)

    for filename in filenames[:10]:  # оценим производительность на первых 10 файлах
        start_time = time.time()
        spec1, spec2 = get_spectrogram_pair_v1(folder_path=folder_path, filenames=[filename])
        end_time = time.time()

        execution_time = end_time - start_time
        print(f"FFT для файла {filename} выполнено за {execution_time} секунд")
