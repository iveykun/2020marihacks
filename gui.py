import PySimpleGUI as sg
import pytesseract
from PIL import Image
import os
import sys
import speech_recognition as sr
import moviepy.editor as mp
import time
from pydub import AudioSegment
from pydub.silence import split_on_silence
from rake_nltk import Rake
import nltk
from nltk import ne_chunk
from nltk.tokenize import word_tokenize
import random




'''THIS IS THE QUIZ PART'''

def dt(txt="Notes.txt"):  # remember to add quotes ex: dt('corona.txt')
    r = Rake(min_length=2, max_length=3) # only takes terms with 2-3 words in them, ex. Thomas Edison, John F Kennedy
    text = open(str(txt))
    #text = open(input())
    temp = text.read()
    textcopy = str(temp)

    #text = 

    keywords = r.extract_keywords_from_text(str(textcopy))  # finds keywords, usually a lot of words

    lst = []
    with_score = r.get_ranked_phrases()  # output the keywords you found


    keywords

    for word in with_score:
        lst.append(word)  # appends all keywords found to lst
    lst = lst[0:50:2]   # removing half of them in steps of 2 to avoid having too many blanks in one sentence
    #print(lst)
    dic = {}
    for count, thing in enumerate(lst):
        dic[count] = thing
        replace = ' _________{}{}{} '.format('[', count, '] ') 
        textcopy = textcopy.replace(thing, replace)  # replacing the keywords with blanks
    #textcopy.replace('thinking', '________')
    f = open("Quiz.txt", "w+")
    f.write(textcopy)  # writing final text to txt
    
    f.write('\n')
    f.write('\n')
    f.write('answers:')
    f.write('\n')
    for item in dic.items():
        f.write(str(item))
        f.write('\n')
    
    f.close()
    #print(textcopy)
    # reveal('abilities', 18, dic)  # you need to put them in this order 
    return dic

def reveal(answer, num, dic):  # get answer, tells if it's right
    real = dic.get(num)
    
    fin = open("Quiz.txt", 'r') # make it change the text in the file when asked for answer
    fout = open("Corrected.txt", 'w')
    need = ' __{}__{}{}{} '.format(real, '[', num, '] ')
    for line in fin:
        look = ' _________{}{}{} '.format('[', num, '] ')
        if look in line:
            newline = line.replace(look, real)
            fout.write(newline)
        else:
            fout.write(line)
    fin.close()
    fout.close()
    
    if answer in real:
        
        feedback = "Correct! The answer is " + real
        return feedback
    else:
        feedback = "Wrong! The answer is " + real  
        return feedback
        
        
        
'''THIS IS THE SPEECH PART'''

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
    print("Splitting file...")
    stime = time.time()
    chunks = split_on_silence(
        soundstream, 
        min_silence_len=400, 
        # Silence threshold is deliberatly low
        # to enable lots of possible cuts 
        silence_thresh=silence_threshold, 
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
def tts_from_file(source_file):
    r = sr.Recognizer()
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

# constant string to facilitate file interoperability
def recon_speech(filename="Talking.mp4", chunk_size=30, silence_threshold=-45):
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
    start = time.time()
    # Avoids spliting the Audiofile if its short enough
    if not need_cut:
        try:
            temp_string = tts_from_file(wavfile)
            out_string += temp_string
        except ValueError:
            need_cut = True
            # Resets output string
            out_string = ""
    if need_cut:
        filelist = cut_audio(wavfile, chunk_size, silence_threshold)
        maxlen = len(filelist)
        index = 1
        for audio_file in filelist:
            print("Processing chunk " + str(index) + " of "  + str(maxlen))
            try:
                temp_string = tts_from_file(audio_file)
                out_string += temp_string
            except:
                print("Skipped file " + audio_file + " in chunk list")
            index+=1
    elapsed = time.time() - start
    #For logging purposes
    print(out_string + " in " + str(elapsed) + " seconds", end="\r")
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
    print(response.text)
    f=open("Notes.txt","w+")
    f.write(response.text)
    f.close()
    cleanup(filelist)
    # Returns 0 in case of sucess, as is tradition 
    return 0

'''THIS IS THE UI PART'''
def Opening():
    sg.theme('Reddit')
    layout = [  [sg.Text('Hi! My name is Etika-Sensei, and I will be your substitute teacher.')],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Happy.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        elif event in (None, 'Ok'):
            window.close()
            Opening2()
            break
    window.close()


def Opening2():
    sg.theme('Reddit')    
    layout = [  [sg.Text('So it seems like you skipped class again...  Thankfully, we can still recover if you have notes/the lecture.')],
                [sg.Text('If you give me a video of the lecture you missed, or a copy of handwritten notes, I will be able to create a quiz for you!')],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Doom.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        elif event in (None, 'Ok'):
            window.close()
            Main()
            break
    window.close() 
def Main():
    sg.theme('Reddit')	# Add a touch of color
    # All the stuff inside your window.
    layout = [  [sg.Text('Do you have a video or notes?')],
                [sg.Text('Video/Notes'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Blush.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    
    # Create the Window    
    window = sg.Window('Etika-Sensei', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        else:
            print(values[0])
            if values[0]== "Notes":
                window.close()
                Text()
            elif values[0]=="Video":
                window.close()
                Video()
            else:
                print("Invalid input")

    window.close()
    
def Text():
    sg.theme('Reddit')
    layout = [  [sg.Text('What is the name of your image file?')],
                [sg.Text('Name'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Happy.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        else:
            try:
                image= values[0]
                img = Image.open(image)
            except IOError:
                print("Invalid input")
                window.close()
                Text()
            finally:
                window.close()
                sg.theme('Reddit')
                layout = [  [sg.Text('Alright just give me a second and I will turn these into a text file. ')],
                            [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Blush.png')],
                            [sg.Button('Ok'),sg.Button('Cancel')] ]
                window = sg.Window('Etika-Sensei', layout)
                event, values = window.read()
                if event in (None, 'Cancel'):	# if user closes window or clicks cancel
                    window.close()
                    break
                else:
                    print("Apple")
                    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
                    print( pytesseract.image_to_string(img) )
                    f=open("Notes.txt","w+")
                    f.write(pytesseract.image_to_string(img))
                    f.close()
                    window.close()
                    QuizAsk()
                    break
                     
    window.close()
    
def Video():
    sg.theme('Reddit')
    layout = [  [sg.Text('What is the name of the video file?')],
                [sg.Text('Video/Text'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Happy.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)

    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            window.close()
            break
        else:
            name=values[0]
            print(name)
            window.close()
            sg.theme('Reddit')
            layout = [  [sg.Text('Alright just give me a second and I will turn these into a text file. ')],
                        [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Blush.png')],
                        [sg.Button('Ok'),sg.Button('Cancel')] ]
            window = sg.Window('Etika-Sensei', layout)
            event, values = window.read()
                
            if event in (None, 'Cancel'):	# if user closes window or clicks cancel
                window.close()
                break
            else:
                print("Apple")
                recon_speech(name)
                window.close()
                QuizAsk()
                break

def QuizAsk():
    sg.theme('Reddit')
    layout = [  [sg.Text('I just finished making a note file from what you gave me.')],
                [sg.Text('Do you want me to quiz you on that?')],
                [sg.Text('Yes/No'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Happy.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)  
    
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            break
        else:
            print(values[0])
            if values[0]== "Yes":
                window.close()
                Quiz()
                break
            elif values[0]=="No":
                window.close()
                Thanks()
            else:
                print("Invalid input")

    window.close()
    

def Quiz():
    sg.theme('Reddit')
    layout = [  [sg.Text('Ok!')],
                [sg.Text('The Quiz is in a folder called Quiz.txt')],
                [sg.Text('Give me the answers and I will correct you.')],
                [sg.Text('Number'), sg.InputText()],
                [sg.Text('Answer'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Blush.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)
    dic = dt()
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            window.close() 
            break
        else:
            if "Correct" in reveal(values[1],int(values[0]),dic):
                window.close()
                Right(reveal(values[1],int(values[0]),dic))
            else:
                window.close()
                Wrong(reveal(values[1],int(values[0]),dic))
    
                
def Right(feedback):
    sg.theme('Reddit')
    layout = [  [sg.Text(feedback)],
                [sg.Text('Number'), sg.InputText()],
                [sg.Text('Answer'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Happy.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)
    dic = dt()
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            window.close() 
            break
        else:
            if "Correct" in reveal(values[1],int(values[0]),dic) :
                window.close()
                Right(reveal(values[1],int(values[0]),dic))
            else:
                window.close()
                Wrong(reveal(values[1],int(values[0]),dic))
    
def Wrong(feedback):
    sg.theme('Reddit')
    layout = [  [sg.Text(feedback)],
                [sg.Text('Number'), sg.InputText()],
                [sg.Text('Answer'), sg.InputText()],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Diss.png')],
                [sg.Button('Ok'), sg.Button('Cancel')] ]
    window = sg.Window('Etika-Sensei', layout)
    dic = dt()
    while True:
        event, values = window.read()
        if event in (None, 'Cancel'):	# if user closes window or clicks cancel
            window.close() 
            break
        else:
            if "Correct" in reveal(values[1],int(values[0]),dic):
                window.close()
                Right(reveal(values[1],int(values[0]),dic))
            else:
                window.close()
                Wrong(reveal(values[1],int(values[0]),dic))
    
        
    
    
def Thanks():
    sg.theme('Reddit')
    layout = [  [sg.Text('Ok, no problem! Thanks for using me and make sure to study the notes I made for you!')],
                [sg.Image(r'C:\Users\lotfi\Desktop\Marihacks\UI\Program\Images\Blush.png')],
                [sg.Button('Ok'), sg.Button('Bye')] ]
    window = sg.Window('Etika-Sensei', layout)
    while True:
        event, values = window.read()
        if event in (None, 'Bye'):	# if user closes window or clicks cancel
            window.close()
            break
Opening()

