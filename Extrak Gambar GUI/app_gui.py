from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import sqlite3

# Konfigurasi path tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Setup database
conn = sqlite3.connect('history.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS extractions (image_path TEXT, extracted_text TEXT)''')
conn.commit()

# Abstraksi & Inheritance
class BaseExtractor:
    def extract(self, image_path):
        raise NotImplementedError("Method extract() harus dioverride")

# Polimorfisme
class TesseractExtractor(BaseExtractor):
    def extract(self, image_path):
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)

# GUI Aplikasi
class TextExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text Extractor from Image")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f7")

        self.__image_path = None
        self.__tk_img = None
        self.extractor = TesseractExtractor()

        self.setup_ui()

    def setup_ui(self):
        Label(self.root, text="Text Extractor from Image", font=("Helvetica", 18, "bold"), bg="#f0f4f7").pack(pady=10)

        Button(self.root, text="Upload Image", command=self.upload_image, bg="#4CAF50", fg="white", padx=10, pady=5).pack()

        self.img_label = Label(self.root, bg="#d3d3d3", width=400, height=300)
        self.img_label.pack(pady=10)

        Button(self.root, text="Extract Text", command=self.extract_text, bg="#2196F3", fg="white", padx=10, pady=5).pack(pady=5)

        text_frame = Frame(self.root)
        text_frame.pack(padx=20, pady=10, fill=BOTH, expand=True)

        self.text_output = Text(text_frame, wrap=WORD, height=8, font=("Arial", 12))
        self.text_output.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(text_frame, command=self.text_output.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_output.config(yscrollcommand=scrollbar.set)

        Button(self.root, text="📜 Lihat Histori", font=("Segoe UI", 14, "bold"), fg="white", bg="#004080",
               relief=RAISED, cursor="hand2", command=self.view_history).pack(pady=15, ipadx=20, ipady=10)

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.__image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((400, 300))
            self.__tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.__tk_img)

    def extract_text(self):
        if not self.__image_path:
            messagebox.showwarning("No image", "Please upload an image first.")
            return

        extracted_text = self.extractor.extract(self.__image_path)

        self.text_output.delete(1.0, END)
        self.text_output.insert(END, extracted_text)

        c.execute("INSERT INTO extractions VALUES (?, ?)", (self.__image_path, extracted_text))
        conn.commit()

    def view_history(self):
        history_window = Toplevel(self.root)
        history_window.title("Histori Ekstraksi")
        history_window.geometry("650x500")

        canvas = Canvas(history_window)
        scrollbar = Scrollbar(history_window, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)

        c.execute("SELECT rowid, * FROM extractions ORDER BY rowid DESC")
        records = c.fetchall()

        for record in records:
            rowid, image_path, extracted_text = record

            container = Frame(scrollable_frame, bd=1, relief=SOLID, padx=10, pady=10, bg="white")
            container.pack(fill=X, padx=10, pady=10)

            Label(container, text=f"Image Path: {image_path}", font=("Arial", 10, "bold"), bg="white").pack(anchor=W)

            entry = Text(container, height=10, wrap=WORD)
            entry.insert(END, extracted_text)
            entry.pack(fill=X, padx=5, pady=5)

            # Tombol edit
            Button(container, text="✏ Edit", bg="#f1c40f", fg="black", padx=5, command=lambda e=entry, i=rowid: self.edit_entry(e, i)).pack(side=LEFT, padx=5)

            # Tombol hapus
            Button(container, text="🗑 Hapus", bg="#e74c3c", fg="white", padx=5, command=lambda i=rowid, f=container: self.delete_entry(i, f)).pack(side=LEFT)

        Button(scrollable_frame, text="🗑 Hapus Semua", font=("Segoe UI", 12, "bold"),
               bg="#c0392b", fg="white", padx=10, pady=5,
               command=lambda: self.clear_all_history(scrollable_frame)).pack(pady=20)

    def edit_entry(self, text_widget, rowid):
        new_text = text_widget.get("1.0", END).strip()
        if new_text:
            c.execute("UPDATE extractions SET extracted_text = ? WHERE rowid = ?", (new_text, rowid))
            conn.commit()
            messagebox.showinfo("Berhasil", "Teks berhasil diperbarui.")
        else:
            messagebox.showwarning("Peringatan", "Teks tidak boleh kosong.")

    def delete_entry(self, rowid, frame_widget):
        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus entri ini?"):
            c.execute("DELETE FROM extractions WHERE rowid = ?", (rowid,))
            conn.commit()
            frame_widget.destroy()
            messagebox.showinfo("Berhasil", "Entri berhasil dihapus.")

    def clear_all_history(self, parent_frame):
        if messagebox.askyesno("Konfirmasi", "Apakah Anda yakin ingin menghapus semua histori?"):
            c.execute("DELETE FROM extractions")
            conn.commit()
            for widget in parent_frame.winfo_children():
                widget.destroy()
            messagebox.showinfo("Histori", "Semua histori berhasil dihapus.")

# Main
if __name__ == "__main__":
    root = Tk()
    app = TextExtractorApp(root)
    root.mainloop()
    conn.close()
