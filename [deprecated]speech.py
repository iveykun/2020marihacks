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
    apple=r.recognize_google(audio)
    print(apple)


f=open("Lesson.txt","w+")

f.write(apple)
f.close()


