from pyvad import vad


def detect_voice(audio, sr):
    vact = vad(audio, sr, vad_mode=3, hoplength=30)
    return vact
