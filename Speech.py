#!/usr/bin/env python3
import os
import sys
import speech_recognition as sr
import moviepy.editor as mp

clip = mp.VideoFileClip("Talking.mp4")
length = clip.duration
clip.audio.write_audiofile("talkingaudio.wav")

r=sr.Recognizer()
# Small file optimization
# Skips the tentative Google API step for files
# of known short length by setting the sphinx flag
if length > 120:
    sphinx = True
else:
    sphinx = False
audio_file = sr.AudioFile("talkingaudio.wav")
with audio_file as source:
    audio = r.record(source)
    if not sphinx:
        try:
            recognized_text=r.recognize_google(audio)
        # Handles case for unrecognizable speech
        except sr.UnknownValueError:
            print("Google API could not recognize speech")
            sys.exit(125)
        except sr.RequestError as error:
            # Changing speech recognition back-end if Google refuses our request
            print("Could not perform the request, Google Web-Speech API: {0}".format(error))
            print("Switching to Sphinx...")
            sphinx = True
    if sphinx:
        try:
            recognized_text=r.recognize_sphinx(audio)
        except sr.UnknownValueError:
            print("Sphinx API failed to recognize speech")
            sys.exit(125)
        except sr.RequestError as error:
            print("Sphinx API Error : {0}".format(error))
            sys.exit(125)
    #For logging purposes
    print(recognized_text)
    import requests
    data = {'text':recognized_text}
    # Uses the following website to generate punctuated file
    try:
        response = requests.post('http://bark.phon.ioc.ee/punctuator', data=data)
    except:
        sys.exit(126)
    # 200 Corresponds to HTML response code OK
    if response.status_code != 200:
        # Exits the program on erronous request
        print("Incomplete request, Error code: " + response.status_code )
        sys.exit(127)
    #Logging purposes
    print(response.text)
f=open("Lesson.txt","w+")
f.write(response.text)
f.close()
