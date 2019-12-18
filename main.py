#!/usr/bin/env python
import io

# Imports the Google Cloud client library
from google.cloud import speech

# Instantiates a client
speech_client = speech.Client()

# The name of the audio file to transcribe
transcriptionPath = '/usr/voicemailtranscription/transcription/'
audioPath = '/usr/voicemailtranscription/voicemail/'
audioFileName = 'test.wav'
file_name = audioPath+audioFileName

# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio_sample = speech_client.sample(
        content,
        source_uri=None,
        encoding='LINEAR16',
        sample_rate=44100)

# Detects speech in the audio file
alternatives = speech_client.speech_api.sync_recognize(audio_sample)

for alternative in alternatives:
    print('Transcript: {}'.format(alternative.transcript))