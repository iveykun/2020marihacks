#!/usr/bin/env python3
#### FOR DEVELOPMENT & TESTING PURPOSES ####
import os
import asyncio
import sys
import speech_recognition as sr
import moviepy.editor as mp
import time
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Cuts audio in ~120 seconds chunks where the cut corresponds
# to a silence in the audio stream
# input arg: file path of .wav file
#            chunk_size corresponds to the target size of the 
#            sliced chunk. Lower seems to be better
#            silence_threshold corresponds to the volume considered 
#            silence by the pydub function.
#            Lower means quieter;
# note:      file must be in the directory of program
def cut_audio(audiofile, chunk_size=30, silence_threshold=-45):
    soundstream = AudioSegment.from_wav(audiofile)
    # Splits wav file on silence
    # to an array of AudioSegments
    # contained in chunks
    print(str(soundstream.dBFS) +  " and " + str(soundstream.max_dBFS))
    print("Splitting file...")
    stime = time.time()
    chunks = split_on_silence(
        soundstream, 
        min_silence_len=400, 
        # Silence threshold is deliberatly low
        # to enable lots of possible cuts 
        silence_thresh=silence_threshold,
        keep_silence=200
    )
    etime = time.time() - stime
    print("...in " + str(etime) + " seconds")
    # Unable to find any silence
    if chunks == []:
        print("Unable to find silence!")
        return [audiofile]
    else:
        chlen = len(chunks)
    # Target length of chunks cuts
    # in milliseconds. Small enough to accepted by the 
    # Google Web Speech to Text API
    out_len = chunk_size*1000
    out_chunks = [chunks[0]]
    i = 0 
    for chunk in chunks[1:]:
        print("Recombining " + str(i) + " on " + str(chlen), end="\r")
        # Appends a new chunk to the last if it is too short
        if len(out_chunks[-1]) < out_len:
            out_chunks[-1] += chunk
        # Appends a chunk to the output array if its length is ok
        else:
            out_chunks.append(chunk)
        i += 1
    out_list = []
    i = 0
    for newchunk in out_chunks:
        # Adds silence to chunks by concatenating AudioSegments
        silence = AudioSegment.silent(duration=10)
        audio_chunk = silence + newchunk + silence
        # Wav files are the way to provide interoperability between
        # the different audio libraries (pydub, SpeechRecognition, pymovie)
        # They will be deleted at program exit
        # Format:   Each chunk of audio is outputted in its seperate 
        #           chunkN.wav where N corresponds to its chunk
        #           index.
        audio_chunk.export( "./chunk{0}.wav".format(i),
                            bitrate = '192k', 
                            format="wav")
        # Forms a list of the chunk filenames
        # which is the the interface between the program
        # and the chunkN.wav files
        filename = 'chunk'+str(i)+'.wav'
        out_list.append(filename)
        i += 1

    return out_list

# It just works(tm)
# Takes source file and converts it to text
# using python SpeechRecognition's built-it API key
# for Google Web Speech to Text API
# note : assumes file is in directory of program
# note2: Avoid high-volume requests  
async def tts_from_file_async(source_file, index, loop):
    r = sr.Recognizer()
    with sr.AudioFile(source_file) as source:
        audio = r.record(source)
        try:
            recognized_text = await loop.run_in_executor(None, r.recognize_google, audio)
        # Handles case for unrecognizable speech
        except sr.UnknownValueError:
            print("Google API could not recognize speech")
            sys.exit(125)
        except sr.RequestError as error:
            # Changing speech recognition back-end if Google refuses our request
            print("Could not perform the request, Google Web-Speech API: {0}".format(error))
            raise ValueError
        except Exception as error:
            print("Other Error : {0}".format(error))
        #For logging purposes
        # print(recognized_text)
        if isinstance(recognized_text, str):
            return (index, recognized_text)
        else:
            raise ValueError("Recognized Text not a string!")

async def tts_async_manager(files, loop):
    operations = []
    index = 0
    for audiofile in files:
        operation = asyncio.create_task(tts_from_file_async(audiofile, index, loop))
        operations.append(operation)
        index += 1
    return await asyncio.gather(*operations, return_exceptions=True)

# Cleanup.
# Deletes temporary chunk files and pymovie conversion result
# Appends temporary converted file to enable single-loop cleanup
def cleanup(filelist):
    for wfile in filelist:
        if os.path.exists(wfile):
            os.remove(wfile)

#######################
#__   __       _
#|  \/  | __ _(_)_ __
#| |\/| |/ _` | | '_ \
#| |  | | (_| | | | | |
#|_|  |_|\__,_|_|_| |_|
#######################

def recon_speech(filename="Talking.mp4", chunk_size=30, silence_threshold=-35):
    wavfile = "tempwavaudio.wav"
    clip = mp.VideoFileClip(filename)
    length = clip.duration
    clip.audio.write_audiofile(wavfile)

    if length > 120:
        need_cut = True
    else:
        need_cut = False
    out_string = ""
    # Measuring TTS time
    start = 0
    # Avoids spliting the Audiofile if its short enough
    if not need_cut:
        try:
            temp_string = tts_from_file_async(wavfile, -1)
            out_string += temp_string[1]
        except ValueError:
            need_cut = True
            # Resets output string
            out_string = ""
    if need_cut:
        filelist = cut_audio(wavfile, chunk_size, silence_threshold)
        maxlen = len(filelist)
        out_dict = {}
        start = time.time()
        loop = asyncio.get_event_loop()
        string_tuples = loop.run_until_complete(tts_async_manager(filelist, loop))
        out_dict = dict((x,y) for x, y in string_tuples)
        # String repiecement
        for elem in sorted(out_dict.items()):
            out_string += elem[1]
    #For logging purposes
    elapsed = time.time() - start
    print("TTS in " + str(elapsed))
    #print(out_string + " in " + str(elapsed) + " seconds", end="\r")
    import requests
    data = {'text':out_string}
    # Uses the following website to generate punctuated file
    try:
        response = requests.post('http://bark.phon.ioc.ee/punctuator', data=data)
    except:
        cleanup(filelist)
        sys.exit(126)
    # 200 Corresponds to HTML response code OK
    if response.status_code != 200:
        # Exits the program on erronous request
        print("Incomplete request, Error code: " + response.status_code )
        cleanup(filelist)
        sys.exit(127)
    #Logging purposes
    #print(response.text)
    f=open("LessonAsync.txt","w+")
    f.write(response.text)
    f.close()
    cleanup(filelist)
    # Returns 0 in case of sucess, as is tradition 
    return 0
#### FOR TESTING PURPOSES ONLY ####
recon_speech()
