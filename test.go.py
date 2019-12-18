import io
import os
import subprocess

# Imports the Google Cloud client library
#from google.cloud import speech
#from google.cloud.speech import enums
#from google.cloud.speech import types

#result = 'No transcription'

#print('try speech api')

# Instantiates a client
#client = speech.SpeechClient()

# The name of the audio file to transcribe
#file_name = 'C:/inetpub/git/sipxecs-voicemail-transcription/6FWSVU8D24KJPNHYDW4X.wav'
file_name = '/usr/voicemailtranscription/voicemail/6FWSVU8D24KJPNHYDW4X.wav'

result = ""

try:
    #result = subprocess.check_output(['C:/inetpub/git/sipxecs-voicemail-transcription/go/transcription.exe', file_name], shell=True, encoding='utf-8')
    result = subprocess.check_output(['/usr/voicemailtranscription/go/./transcription', file_name],encoding='utf-8')
except Exception as e:
    print(e)
    result = "Transcription unavailable"

print(result)

''' 
# Loads the audio into memory
with io.open(file_name, 'rb') as audio_file:
    content = audio_file.read()
    audio = types.RecognitionAudio(content=content)
    
print('audo defined')

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    #sample_rate_hertz=samplerate,
    language_code='en-US'
)

print('trying recognize request')

response = client.recognize(config, audio)

print('we have response')

alternatives = response.results[0].alternatives

for alternative in alternatives:
    result = format(alternative.transcript)
    print('Transcript: {}'.format(alternative.transcript))

print(result) '''
