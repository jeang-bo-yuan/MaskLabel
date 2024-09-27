from image_edit_window import ImageEditWindow
import tkinter as tk
from tkinter import filedialog

def main():
    root = tk.Tk()
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    img_edit = ImageEditWindow(root
                               , filedialog.askopenfilename(filetypes=[("img", ["*.jpg", "*.png", "*.tif"])])
                               )
    img_edit.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W, tk.E))

    root.geometry("=400x400+20+20")
    root.mainloop()

if __name__ == "__main__":
    main()