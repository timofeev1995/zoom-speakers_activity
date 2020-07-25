from pathlib import Path
from typing import Dict

import numpy as np
import matplotlib.pyplot as plt


def plot_speaker_activity(
        full_audio: np.ndarray,
        padded_audios: Dict[str, np.ndarray],
        speaking_activity: Dict[str, np.ndarray],
        sr: int,
        dump_path: Path
) -> None:

    time = np.linspace(0, len(full_audio) / sr, len(full_audio))
    num_figures = len(padded_audios) + 1

    fig, axs = plt.subplots(
        num_figures, 1,
        constrained_layout=True,
        figsize=(18, 3 * (num_figures + 1)),
        sharex=True,
        sharey=True
    )
    axs[0].plot(time, full_audio, color='black')
    axs[0].set_title('Full audio', fontsize='large')
    axs[0].set_xlabel('Time in seconds', fontsize='medium')

    for n, (speaker_name, audio) in enumerate(padded_audios.items()):
        activity = speaking_activity[speaker_name]

        axs[n + 1].plot(time, audio)
        axs[n + 1].set_title(speaker_name, fontsize='large')
        axs[n + 1].set_xlabel('Time in seconds', fontsize='medium')

        axs_additional = axs[n + 1].twinx()
        axs_additional.plot(time, activity, color='r', alpha=0.7)
        axs_additional.set_yticks([0, 1.1])
        axs_additional.set_ylim([-0.01, 1.01])

    plt.savefig(dump_path)
