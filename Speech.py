#!/usr/bin/env python3
import os
import speech_recognition as sr
import moviepy.editor as mp


clip = mp.VideoFileClip("Talking.mp4")
clip.audio.write_audiofile("talkingaudio.wav")


r=sr.Recognizer()

audio = sr.AudioFile("talkingaudio.wav")
with audio as source:
    audio = r.record(source, duration=100)
    recognized_text=r.recognize_google(audio)
    #For logging purposes
    print(recognized_text)
    import requests
    data = {'text':recognized_text}
    response = requests.post('http://bark.phon.ioc.ee/punctuator', data=data)

f=open("Lesson.txt","w+")
if isinstance(response, basestring):
    f.write(apple)
f.close()


