import librosa
import os
import numpy as np
import matplotlib.pyplot as plt


def get_audio_sample(audio, sr: float, start: float, duration: float):
    return audio[start * sr:(start + duration) * sr]


def get_spectrogram_sample(
        audio,
        sr: float,
        start: float,
        duration: float,
        volume: float = 1,
        frame_size: int = 2048,
        hop_size: int = 512
):

    sample = get_audio_sample(audio, sr, start=start, duration=duration) * volume
    return librosa.stft(sample, n_fft=frame_size, hop_length=hop_size)


def get_spectrograms(audio, sr: float, n_samples: int, start: float, duration: float, overlap: float):
    spectrograms = []
    for i in range(n_samples):
        spec = get_spectrogram_sample(
            audio=audio,
            sr=sr,
            start=start + i*(duration - overlap),
            duration=duration
        )
        spectrograms.append(spec)

    return spectrograms


def plot_spectrograms(spectrograms, sr: float):
    plt.figure(figsize=(8, 3))

    plt.subplot(2, 1, 1)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spectrograms[0]), ref=np.max), sr=sr, y_axis='log', x_axis='time')
    # plt.title('Spectrogram 1')
    # plt.colorbar(format='%+2.0f dB')

    plt.subplot(2, 1, 2)
    librosa.display.specshow(librosa.amplitude_to_db(np.abs(spectrograms[1]), ref=np.max), sr=sr, y_axis='log', x_axis='time')
    # plt.title('Spectrogram 2')
    # plt.colorbar(format='%+2.0f dB')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    folder_path = r'D:\PROGRAMMS\PYTHON_PROJECTS\youtube_parse\tracks_wav'
    filenames = os.listdir(folder_path)

    y, sr = librosa.load(os.path.join(folder_path, filenames[0]), sr=44100, mono=True)
    sp = get_spectrograms(y, sr, 2, 30, 30, 25)
    plot_spectrograms(sp, sr)
    # librosa.display.specshow(librosa.amplitude_to_db(np.abs(sp[0]), ref=np.max), sr=sr, y_axis='log', x_axis='time')
    # plt.colorbar(format='%+2.0f dB')

    # plt.show()


