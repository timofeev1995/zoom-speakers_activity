import os
from pathlib import Path
from typing import Tuple, Dict

import librosa
import numpy as np
from pydub import AudioSegment
from tqdm import tqdm

from src.defaults import MEL_SPEC_POWER, N_MELS, N_FFT, HOP_LENGTH
from src.utils import _mae, _get_speakername_from_filename
from src.vad import detect_voice


def _calculate_melspec(y: np.ndarray, sr: int) -> np.ndarray:
    return librosa.feature.melspectrogram(
        y=y,
        sr=sr,
        n_mels=N_MELS,
        power=MEL_SPEC_POWER,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH
    )


def _find_start_timestamp(full_mel: np.ndarray, speaker_mel: np.ndarray) -> int:
    speaker_mel_lenght = len(speaker_mel)
    diff = len(full_mel) - speaker_mel_lenght
    min_distance = np.inf
    result_index = 0
    for sep in tqdm(range(diff)):
        current_distance = _mae(
            speaker_mel, full_mel[sep:speaker_mel_lenght+sep]
        )
        if current_distance < min_distance:
            result_index = sep
            min_distance = current_distance
    return result_index


def _pad_track(
        audio: np.ndarray,
        sr: int,
        position: np.ndarray,
        to_length: int
) -> np.ndarray:
    position = np.concatenate([position, np.array([to_length])])
    position_time = librosa.core.samples_to_time(position, sr=sr)

    left_padding_length = position_time[0] * 1000
    left_padding = AudioSegment.silent(duration=left_padding_length, frame_rate=sr)

    right_padding_length = (position_time[2] - position_time[1]) * 1000
    right_padding = AudioSegment.silent(duration=right_padding_length, frame_rate=sr)

    audio_to_return = np.concatenate(
        [
            np.array(left_padding.get_array_of_samples()),
            audio,
            np.array(right_padding.get_array_of_samples())
        ]
    )

    tail_padding = np.zeros(to_length - len(audio_to_return))
    audio_to_return = np.concatenate([audio_to_return, tail_padding])

    return audio_to_return


def load_recorded_zoom_data(
        path_to_recorded: Path
) -> Tuple[np.ndarray, Dict[str, np.ndarray], int]:

    full_audio, sr = librosa.load(str(path_to_recorded / 'audio_only.m4a'))
    full_audio_length = len(full_audio)

    speaker_audios = {}
    for speaker_filename in os.listdir(path_to_recorded / 'Audio Record/'):
        speaker_name = _get_speakername_from_filename(speaker_filename)
        speaker_audio, _ = librosa.load(str(path_to_recorded / 'Audio Record/' / speaker_filename))
        if len(speaker_audio) != full_audio_length:
            speaker_audios.update({speaker_name: speaker_audio})
        else:
            speaker_audios.update({'host': speaker_audio})

    return full_audio, speaker_audios, sr


def pad_speaker_audios(
        full_audio: np.ndarray,
        speaker_audios: Dict[str, np.ndarray],
        sr: int
) -> Dict[str, np.ndarray]:

    full_audio_lenght = len(full_audio)
    full_mel_spec = _calculate_melspec(y=full_audio, sr=sr)

    padded_tracks = {}
    for speaker, audio in speaker_audios.items():
        speaker_mel = _calculate_melspec(y=audio, sr=sr)

        start_index = _find_start_timestamp(
            full_mel=full_mel_spec.T,
            speaker_mel=speaker_mel.T
        )
        end_index = start_index + speaker_mel.shape[1]

        if start_index != 0:
            position_of_speaker_audio = librosa.core.frames_to_samples(
                frames=np.array([start_index, end_index]),
                hop_length=HOP_LENGTH,
                n_fft=N_FFT
            )
            padded_audio = _pad_track(
                audio=audio,
                sr=sr,
                position=position_of_speaker_audio,
                to_length=full_audio_lenght
            )
        else:
            padded_audio = audio

        padded_tracks[speaker] = padded_audio

    return padded_tracks


def get_speaking_activity(
        audios: Dict[str, np.ndarray],
        sr: int,
        pad_to: int
) -> Dict[str, np.ndarray]:

    activities = {}
    for speaker, audio in audios.items():
        activity = detect_voice(audio, sr)
        activity = np.concatenate([activity, np.zeros(pad_to - len(activity))])
        activities[speaker] = activity

    return activities
