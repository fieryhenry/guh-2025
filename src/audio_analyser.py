def read_file(filename):
    print(f"Reading: {filename}")
    return librosa.load(filename)


def get_bpm(audiodata):
    return librosa.beat.beat_track(y=audiodata[0], sr=audiodata[1])[0]


def get_key(audiodata):
    chromagram = librosa.feature.chroma_stft(y=audiodata[0], sr=audiodata[1])
    mean_chroma = np.mean(chromagram, axis=1)
    keys = librosa.key_to_notes("A:maj")
    estimated_key = keys[np.argmax(mean_chroma)]

    return estimated_key


def split_audio(audiodata, start, duration):
    return audiodata[start * audiodata[1] : duration * audiodata[1]]


def match_bpm(audiosource, audioreference):
    multiply_factor = get_bpm(audioreference) / get_bpm(audio_source)
    return librosa.effects.time_stretch(audiosource[0], rate=multiply_factor)


def write_audio_data(audiodata, output_file):
    librosa.write(output_file, audiodata[0], audiodata[1])



if __name__ == "__main__":
    file1 = "piano Edit 1 Export 1.wav"
    file2 = "Pixelated Decay.wav"
    file3 = "H3ll0,W0rlD Export 4.wav"
    print(get_key(split_audio(read_file(file3), 0, 30)))
    write_audio_data(, output_file)
