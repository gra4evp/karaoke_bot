import librosa


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
