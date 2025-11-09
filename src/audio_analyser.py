import librosa
import numpy as np
import soundfile as sf
from pydub import AudioSegment


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


def split_audio(audiodata, start, end):
    return (
        audiodata[0][round(start * audiodata[1]) : round(end * audiodata[1])],
        audiodata[1],
    )


def match_bpm(audiosource, audioreference):
    multiply_factor = get_bpm(audioreference) / get_bpm(audiosource)
    print(multiply_factor)
    return librosa.effects.time_stretch(audiosource[0], rate=multiply_factor)


def write_audio_data(audiodata, output_file, sample_rate=int(44100 / 2)):
    sf.write(output_file, audiodata, sample_rate, subtype="PCM_24")


def pitch_shift(audiodata, steps):
    print(f"Pitch shift by {steps} steps")
    return librosa.effects.pitch_shift(y=audiodata[0], sr=audiodata[1], n_steps=steps)


def find_key_difference(source_audiodata, reference_audiodata):
    key1 = get_key(source_audiodata)
    key2 = get_key(reference_audiodata)

    return librosa.note_to_midi(key2) - librosa.note_to_midi(key1)


def merge_audio(audiofile1, audiofile2):
    audio1 = AudioSegment.from_file(audiofile1, format="wav")
    audio2 = AudioSegment.from_file(audiofile2, format="wav")
    audio1.normalize()
    audio2.normalize()
    merged = audio1.overlay(audio2)
    merged.export("temp1.wav", format="wav")
    return read_file("temp1.wav")


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

    output = []
    for i in range(min(len(audiosource_split), len(audioreference_split)) - 1):
        output.append(
            match_bpm(
                split_audio(
                    audiosource, audiosource_split[i], audiosource_split[i + 1]
                ),
                split_audio(
                    audioreference, audioreference_split[i], audioreference_split[i + 1]
                ),
            )
        )

    return output


if __name__ == "__main__":
    file1 = "piano Edit 1 Export 1.wav"
    file2 = "Pixelated Decay.wav"
    file3 = "H3ll0,W0rlD Export 4.wav"

    print(get_key(split_audio(read_file(file3), 0, 30)))

    bpm_match = match_bpm(read_file(file2), read_file(file1))
    write_audio_data(bpm_match, "out.wav")

    pitch_match = pitch_shift(
        read_file("out.wav"),
        find_key_difference(read_file("out.wav"), read_file(file1)),
    )
    write_audio_data(pitch_match, "out.wav")

    bpm_match = match_bpm_fine(read_file("out.wav"), read_file(file1))

    tempo, beats = librosa.beat.beat_track(
        y=read_file(file1)[0], sr=read_file(file1)[1]
    )
    tempo2, beats2 = librosa.beat.beat_track(
        y=read_file(file2)[0], sr=read_file(file2)[1]
    )

    print(beats)
    print(beats2)

    merged = merge_audio(file1, "out.wav")
    write_audio_data(merged[0], "out.wav")
