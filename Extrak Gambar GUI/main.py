from extractor import TextExtractor
from database import DatabaseHandler
from ui import MainWindow

if __name__ == "__main__":
    extractor = TextExtractor(tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe")  # Ganti sesuai path kamu
    db = DatabaseHandler()
    app = MainWindow(extractor, db)
    app.mainloop()
