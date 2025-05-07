from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import sqlite3

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path if necessary

# Setup database
conn = sqlite3.connect('history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS extractions (image_path TEXT, extracted_text TEXT)''')
conn.commit()

class TextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Extractor from Image")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f7")
        self.image_path = None
        self.tk_img = None

        self.setup_ui()

    def setup_ui(self):
        Label(self.root, text="Text Extractor from Image", font=("Helvetica", 18, "bold"), bg="#f0f4f7").pack(pady=10)

        Button(self.root, text="Upload Image", command=self.upload_image, bg="#4CAF50", fg="white", padx=10, pady=5).pack()

        self.img_label = Label(self.root, bg="#d3d3d3", width=400, height=300)
        self.img_label.pack(pady=10)

        Button(self.root, text="Extract Text", command=self.extract_text, bg="#2196F3", fg="white", padx=10, pady=5).pack(pady=5)

        # Frame pembungkus Text dan Scrollbar
        text_frame = Frame(self.root)
        text_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

        # Text widget untuk hasil ekstraksi
        self.text_output = Text(text_frame, wrap=WORD, height=8, font=("Arial", 12))
        self.text_output.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar untuk Text widget
        scrollbar = Scrollbar(text_frame, command=self.text_output.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_output.config(yscrollcommand=scrollbar.set)

        history_btn = Button(self.root, text="Lihat Histori", font=("Arial", 14), fg="blue", relief=FLAT, command=self.view_history)
        history_btn.pack(padx=20, pady=10, fill=X)
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((400, 300))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img)

    def extract_text(self):
        if not self.image_path:
            messagebox.showwarning("No image", "Please upload an image first.")
            return

        img = Image.open(self.image_path)
        text = pytesseract.image_to_string(img)

        self.text_output.delete(1.0, END)
        self.text_output.insert(END, text)

        c.execute("INSERT INTO extractions VALUES (?, ?)", (self.image_path, text))
        conn.commit()

    def view_history(self):
        history_window = Toplevel(self.root)
        history_window.title("Histori Ekstraksi")
        history_window.geometry("600x400")

        history_text = Text(history_window, wrap=WORD)
        history_text.pack(padx=10, pady=10, fill=BOTH, expand=True)

        scrollbar = Scrollbar(history_window, command=history_text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        history_text.config(yscrollcommand=scrollbar.set)

        c.execute("SELECT * FROM extractions ORDER BY rowid DESC")
        records = c.fetchall()
        for record in records:
            history_text.insert(END, f"Image: {record[0]}\nText:\n{record[1]}\n{'-'*50}\n")

        history_text.config(state=DISABLED)

if __name__ == "__main__":
    root = Tk()
    app = TextExtractorApp(root)
    root.mainloop()
    conn.close()
