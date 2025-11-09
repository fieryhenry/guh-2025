import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment


def read_file(filename):
    print(f"Reading: {filename}")
    return librosa.load(filename)


def get_bpm(audiodata):
    output = librosa.beat.beat_track(y=audiodata[0], sr=audiodata[1])[0][0]
    return output


def get_key(audiodata):
    chromagram = librosa.feature.chroma_stft(y=audiodata[0], sr=audiodata[1])
    mean_chroma = np.mean(chromagram, axis=1)
    keys = librosa.key_to_notes("A:maj")
    estimated_key = keys[np.argmax(mean_chroma)]

    return estimated_key


def split_audio(audiodata, start, end):
    return (
        audiodata[0][round(start * audiodata[1]) : round(end * audiodata[1])],
        audiodata[1],
    )


def match_bpm(audiosource, audioreference):
    multiply_factor = get_bpm(audioreference) / get_bpm(audiosource)
    return librosa.effects.time_stretch(audiosource[0], rate=multiply_factor)


def match_bpm_average(audiodata1, audiodata2):
    multiply_factor = get_bpm(audiodata2) / get_bpm(audiodata1)
    audio1 = librosa.effects.time_stretch(
        audiodata1[0], rate=(1 + (multiply_factor - 1) / 2)
    )
    audio2 = librosa.effects.time_stretch(
        audiodata2[0], rate=(1 + (1 - multiply_factor) / 2)
    )

    return (audio1, audio2)


def write_audio_data(audiodata, output_file, sample_rate=int(44100 / 2)):
    sf.write(output_file, audiodata, sample_rate, subtype="PCM_24")


def pitch_shift(audiodata, steps):
    print(f"Pitch shift by {steps} steps")
    return librosa.effects.pitch_shift(y=audiodata[0], sr=audiodata[1], n_steps=steps)

def pitch_shift2(audiodata, steps):
    new_sample_rate = int(sound.frame_rate) * (2 ** (1/12 * steps))


def pitch_match(audiodata1, audiodata2):
    difference = find_key_difference(audiodata1, audiodata2)
    if difference % 2 == 0:
        difference_half = difference // 2
    else:
        difference_half = difference // 2 + 1

    return (
        pitch_shift(audiodata1, difference // 2),
        pitch_shift(audiodata2, -difference_half),
    )


def find_key_difference(source_audiodata, reference_audiodata):
    key1 = get_key(source_audiodata)
    key2 = get_key(reference_audiodata)

    return librosa.note_to_midi(key2) - librosa.note_to_midi(key1)


def merge_audio(audiofile1, audiofile2):
    audio1 = AudioSegment.from_file(audiofile1, format="wav")
    audio2 = AudioSegment.from_file(audiofile2, format="wav")
    audio1.normalize()
    audio2.normalize()
    if (librosa.get_duration(audio2) > librosa.get_duration(audio1)):
        audio1,audio2 = audio2, audio1

    audio1 += 5
    merged = audio1.overlay(audio2)
    merged.export("temp1.wav", format="wav")
    merged.normalize()
    return read_file("temp1.wav")

def get_harmonic_data(audiodata):
    return librosa.decompose.hpss(librosa.stft(audiodata[0]))[0]

def get_percussion_data(audiodata):
    return librosa.decompose.hpss(librosa.stft(audiodata[0]))[1]

def average_volume(audiodata):
    return np.mean((np.abs(audiodata[0])))


def scale_volume(source_audiodata, reference_audiodata):
    write_audio_data(source_audiodata, "temp1.wav")
    write_audio_data(source_audiodata, "temp2.wav")
    file1 = AudioSegment.from_wav("temp1.wav")
    file2 = AudioSegment.from_wav("temp2.wav")

    print(file2.max, file1.max)
    scaled = file1.apply_gain(file2.max - file1.max)

    scaled.export("temp1.wav", format="wav")
    return read_file("temp1.wav")


def split_bpm(audiodata):
    beats = librosa.beat.beat_track(y=audiodata[0], sr=audiodata[1])[1]
    return librosa.frames_to_time(beats, sr=audiodata[1])


def match_bpm_fine(audiosource, audioreference):
    audiosource_split = split_bpm(audiosource)
    audioreference_split = split_bpm(audioreference)

    output = np.array(audiosource[0])
    for i in range(min(len(audiosource_split), len(audioreference_split)) - 1):
        np.append(
            output,
            (
                match_bpm(
                    split_audio(
                        audiosource, audiosource_split[i], audiosource_split[i + 1]
                    ),
                    split_audio(
                        audioreference,
                        audioreference_split[i],
                        audioreference_split[i + 1],
                    ),
                )[0]
            ),
        )

    return (np.array(output), audiosource[1])


def combine(file1, file2):
    audio1 = read_file(file1)
    audio2 = read_file(file2)

    audiodata1, audiodata2 = match_bpm_average(audio1, audio2)
    write_audio_data(audiodata1, "temp1.wav")
    write_audio_data(audiodata2, "temp2.wav")

    audiodata1, audiodata2 = pitch_match(audio1, audio2)
    write_audio_data(audiodata1, "temp1.wav")
    write_audio_data(audiodata2, "temp2.wav")

    tempaudio = read_file("temp1.wav")
    audiodata1 = pitch_shift(
        tempaudio, find_key_difference(tempaudio, read_file("temp2.wav"))
    )
    write_audio_data(audiodata1, "temp1.wav")

    merged = merge_audio("temp1.wav", "temp2.wav")
    write_audio_data(merged[0], "out.wav")


if __name__ == "__main__":
    file1 = "piano Edit 1 Export 1.wav"
    file2 = "Pixelated Decay.wav"
    file3 = "H3ll0,W0rlD Export 4.wav"

    combine(file1, file3)
