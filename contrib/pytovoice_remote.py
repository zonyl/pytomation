#!/usr/bin/python
"""
Listens for a voice command and sends it to Pytomation
Useful for remote controls with a microphone.
Once the microphone is turned on, google speech recognition
starts listening, and then sends command to Pytomation

Author:
David Heaps - king.dopey.10111@gmail.com
"""
import speech_recognition as sr
import requests
import json
import base64
import time
from sys import byteorder
from array import array

import pyaudio

#constants
THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 22050

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def do_pyto_voice():
    username = "username"
    password = "password"
    server = "http://XXX.XXX.XXX.XXX:XXXX"
    
    r = sr.Recognizer()
    with sr.Microphone() as source:                # use the default microphone as the audio source
        print("Listening for phrase...")
        audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
        print("Thinking about what you said...")
    
    try:
        phrase = r.recognize_google(audio)
    except LookupError:                            # speech is unintelligible
        print("Could not understand audio")
    
    print("You said " + phrase)    # recognize speech using Google Speech Recognition
    phrase = (phrase,)
    command = {'command': phrase}
    r = requests.post(server + "/api/voice", data=json.dumps(command), headers = {'content-type': 'application/json', 
                                                'Authorization': 'Basic ' + base64.b64encode(username + ":" + password)}, verify=False)
    print(r)

#main script
#variables
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=1, rate=RATE,
    input=True, output=False,
    frames_per_buffer=CHUNK_SIZE)
r = array('h')

while 1:
    # little endian, signed short
    snd_data = array('h', stream.read(CHUNK_SIZE))
    if byteorder == 'big':
        snd_data.byteswap()
    r.extend(snd_data)

    silent = is_silent(snd_data)

    if not silent:
        stream.stop_stream()
        stream.close()
        try:
            do_pyto_voice()
        except:
            pass
        stream = p.open(format=FORMAT, channels=1, rate=RATE,
            input=True, output=False,
            frames_per_buffer=CHUNK_SIZE)

