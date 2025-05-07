from PIL import Image
import pytesseract

class TextExtractor:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract(self, image_path):
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
