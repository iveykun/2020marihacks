#!/usr/bin/env python3
import os
import sys
import speech_recognition as sr
import moviepy.editor as mp
import time
from pydub import AudioSegment
from pydub.silence import split_on_silence

def cut_audio(audiofile):
    soundstream = AudioSegment.from_wav(audiofile)
    # Splits wav file on silence
    print("Splitting file...")
    stime = time.time()
    chunks = split_on_silence(
        soundstream, 
        min_silence_len=400, 
        # Silence threshold is deliberatly low
        # since false positive have a much greater impact on sentence
        # structure than false negatives
        silence_thresh=-45, 
    )
    etime = time.time()
    print("...in " + etime + " seconds")
    # Unable to find any silence
    if chunks == []:
        print("Unable to find silence!")
        return [audiofile]
    else:
        chlen = len(chunks)
    out_len = 100*1000
    out_chunks = [chunks[0]]
    i = 0 
    for chunk in chunks[1:]:
        print("Recombining " + str(i) + " on " + str(chlen))
        if len(out_chunks[-1]) < out_len:
            out_chunks[-1] += chunk
        else:
            out_chunks.append(chunk)
        i += 1
    out_list = []
    i = 0
    for newchunk in out_chunks:
        #Adds silence to chunks
        silence = AudioSegment.silent(duration=10)
        audio_chunk = silence + newchunk + silence

        audio_chunk.export( "./chunk{0}.wav".format(i),
                            bitrate = '192k', 
                            format="wav")
        filename = 'chunk'+str(i)+'.wav'
        out_list.append(filename)
        i += 1

    return out_list


def tts_from_file(source_file):
    with sr.AudioFile(source_file) as source:
        audio = r.record(source)
        try:
            recognized_text=r.recognize_google(audio)
        # Handles case for unrecognizable speech
        except sr.UnknownValueError:
            print("Google API could not recognize speech")
            sys.exit(125)
        except sr.RequestError as error:
            # Changing speech recognition back-end if Google refuses our request
            print("Could not perform the request, Google Web-Speech API: {0}".format(error))
            raise ValueError
        #For logging purposes
        # print(recognized_text)
        if isinstance(recognized_text, str):
            return recognized_text
        else:
            raise ValueError("Recognized Text not a string!")



#######################
#__   __       _
#|  \/  | __ _(_)_ __
#| |\/| |/ _` | | '_ \
#| |  | | (_| | | | | |
#|_|  |_|\__,_|_|_| |_|
######################

# constant strings to facilitate file interoperability
wavfile = "tempwavaudio.wav"
clip = mp.VideoFileClip("Talking.mp4")
length = clip.duration
clip.audio.write_audiofile(wavfile)

r=sr.Recognizer()
if length > 120:
    need_cut = True
else:
    need_cut = False
out_string = ""
# Measuring TTS time
start = time.time()
if not need_cut:
    try:
        temp_string = tts_from_file(wavfile)
        out_string += temp_string
    except ValueError:
        need_cut = True
        # Resets output string
        out_string = ""
if need_cut:
    filelist = cut_audio(wavfile)
    maxlen = len(filelist)
    index = 1
    for audio_file in filelist:
        print("Processing chunk " + str(index) + " of "  + str(maxlen))
        try:
            temp_string = tts_from_file(audio_file)
            out_string += temp_string
        except:
            print("Skipped file " + audio_file + " in chunk list")
        i+=1
elapsed = start - time.time()
#For logging purposes
print(out_string + " in " + str(elapsed) " seconds")
import requests
data = {'text':out_string}
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


