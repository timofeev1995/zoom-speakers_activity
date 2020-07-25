import re

import numpy as np


def _mae(a: np.ndarray, b: np.ndarray) -> int:
    return ((a - b) ** 2).mean()


def _get_speakername_from_filename(filename: str) -> str:
    filename_wo_extension = filename.split('.')[0]
    speaker_name = re.split(r'\d._', filename_wo_extension)[-1]
    return speaker_name
