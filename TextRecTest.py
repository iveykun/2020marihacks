import pytesseract
from PIL import Image

image= input("Name of the image: ")
img = Image.open(image)
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'
print( pytesseract.image_to_string(img) )