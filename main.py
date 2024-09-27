from image_edit_window import ImageEditWindow
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

class MainFrame(ttk.Frame):
    """
    主要的視窗，包含圖片顯示的widget（左）和設定參數的widget（右）
    """
    __img_edit__: ImageEditWindow # 圖片顯示視窗

    def __init__(self, master: tk.Misc):
        """
        初始化
        """
        ttk.Frame.__init__(self, master, padding=10)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # 圖片顯示視窗
        self.__img_edit__ = ImageEditWindow(
            self
            , filedialog.askopenfilename(filetypes=[("img", ["*.jpg", "*.png", "*.tif"])])
        )
        self.__img_edit__.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))

    pass # end of class MainFrame

def main():
    root = tk.Tk()

    mainframe = MainFrame(root)
    mainframe.pack(expand=True, fill=tk.BOTH)

    root.geometry("=400x400+20+20")
    root.mainloop()

if __name__ == "__main__":
    main()
