# Load the audio classification pipeline
from transformers import pipeline
import librosa
import soundfile as sf

# Initialize the audio classification pipeline
pipe = pipeline("audio-classification", model="dima806/music_genres_classification")


def classify(filepath: str):
    # Load the first 5 seconds of the audio file
    waveform, sample_rate = librosa.load(filepath, sr=None, duration=6)
    # Save the waveform to a temporary file to use with the pipeline
    temp_filepath = "temp_audio.wav"
    sf.write(temp_filepath, waveform, sample_rate)

    # Use the pipeline directly for classification
    results = pipe(temp_filepath)

    # Extract the predicted genre and confidence
    predicted_genre = results[0]["label"]
    confidence = results[0]["score"]

    print(f"The predicted genre is: {predicted_genre} with confidence {confidence:.2f}")

    return predicted_genre
