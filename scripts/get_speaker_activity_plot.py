import sys
import argparse
import logging
from pathlib import Path

sys.path.append('../')
from src.data import load_recorded_zoom_data, pad_speaker_audios, get_speaking_activity
from src.plot import plot_speaker_activity

logging.basicConfig(level=logging.INFO)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--recordings_folder',
        required=True,
        type=Path,
        help="Path to directory with zoom recording dump"
    )
    parser.add_argument(
        '--plot_dump_path',
        required=True,
        type=Path,
        help="Path to dump of resulting plot"
    )
    args = parser.parse_args()
    return args


def main() -> None:
    logging.info('Parsing command line arguments')
    args = parse_arguments()
    logging.info('Reading audio')
    full_audio, speaker_audios, sr = load_recorded_zoom_data(
        path_to_recorded=Path('../data')
    )
    logging.info('Aligning and padding speaker audio')
    padded_audios = pad_speaker_audios(
        full_audio=full_audio,
        speaker_audios=speaker_audios,
        sr=sr
    )
    logging.info('Calculating speaking intervals using simple VAD')
    speaking_activity = get_speaking_activity(
        audios=padded_audios,
        sr=sr,
        pad_to=len(full_audio)
    )
    logging.info('Plotting results')
    plot_speaker_activity(
        full_audio=full_audio,
        padded_audios=padded_audios,
        speaking_activity=speaking_activity,
        sr=sr,
        dump_path=args.plot_dump_path
    )


if __name__ == '__main__':
    main()

