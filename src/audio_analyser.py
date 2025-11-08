import librosa
import numpy as np
import soundfile as sf
import pydub


def read_file(filename):
    print(f"Reading: {filename}")
    return librosa.load(filename)


def get_bpm(audiodata):
    return librosa.beat.beat_track(y=audiodata[0], sr=audiodata[1])[0][0]


def get_key(audiodata):
    chromagram = librosa.feature.chroma_stft(y=audiodata[0], sr=audiodata[1])
    mean_chroma = np.mean(chromagram, axis=1)
    keys = librosa.key_to_notes("A:maj")
    estimated_key = keys[np.argmax(mean_chroma)]

    return estimated_key


def split_audio(audiodata, start, duration):
    return audiodata[start * audiodata[1] : duration * audiodata[1]]


def match_bpm(audiosource, audioreference):
    multiply_factor = get_bpm(audioreference) / get_bpm(audiosource)
    print(multiply_factor)
    return librosa.effects.time_stretch(audiosource[0], rate=multiply_factor)


def write_audio_data(audiodata, output_file, sample_rate=44100):
    sf.write(output_file, audiodata, sample_rate, subtype="PCM_24")


def pitch_shift(audiodata, steps):
    return librosa.effects.pitch_shift(y=audiodata[0], sr=audiodata[1], n_steps=steps)


def find_key_difference(source_audiodata, reference_audiodata):
    key1 = get_key(source_audiodata)
    key2 = get_key(reference_audiodata)

    return librosa.note_to_midi(key2) - librosa.note_to_midi(key1)


def merge_audio(audiodata1, audiodata2):
    return np.array(librosa.util.stack([audiodata1[0], audiodata2[0]]), audiodata2[1])

def pad_audio(source_audio, reference_audio):
    write_audio_data(source_audio, "temp1.wav")
    write_audio_
    pass


if __name__ == "__main__":
    file1 = "piano Edit 1 Export 1.wav"
    file2 = "Pixelated Decay.wav"
    file3 = "H3ll0,W0rlD Export 4.wav"
    print(get_key(split_audio(read_file(file3), 0, 30)))
    bpm_match = match_bpm(read_file(file2), read_file(file1))
    write_audio_data(bpm_match, "out.wav")
    bpm_match = read_file("out.wav")

    bpm_match = pitch_shift(bpm_match, find_key_difference(read_file(file2), bpm_match))

    write_audio_data(merged, "out.wav")
