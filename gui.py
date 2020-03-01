import PySimpleGUI as sg
import pytesseract
from PIL import Image


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
                pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
                print( pytesseract.image_to_string(img) )
                f=open("Notes.txt","w+")
                f.write(pytesseract.image_to_string(img))
                f.close()
                QuizAsk()
                     
    window.close()



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
                print("Yes")
            elif values[0]=="No":
                window.close()
                print("no")
                Thanks()
            else:
                print("Invalid input")

    window.close()
    
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
