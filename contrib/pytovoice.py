#!/usr/bin/python
"""
Listens for a voice command and sends it to pytomation

Author:
David Heaps - king.dopey.10111@gmail.com
"""
import speech_recognition as sr
import requests
import json
import base64

username = "username"
password = "password"
server = "http://XXX.XXX.XXX.XXX:XXXX"

r = sr.Recognizer()
with sr.Microphone() as source:                # use the default microphone as the audio source
    print("Listening for phrase...")
    audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
    print("Thinking about what you said...")

try:
    phrase = r.recognize(audio)
except LookupError:                            # speech is unintelligible
    print("Could not understand audio")

print("You said " + phrase)    # recognize speech using Google Speech Recognition
phrase = (phrase,)
command = {'command': phrase}
r = requests.post(server + "/api/voice", data=json.dumps(command), headers = {'content-type': 'application/json', 
											'Authorization': 'Basic ' + base64.b64encode(username + ":" + password)})
print(r)
