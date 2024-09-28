from image_edit_window import ImageEditWindow
from control_frame import ControlFrame
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import json

class MainFrame(ttk.Frame):
    """
    主要的視窗，包含圖片顯示的widget（左）和設定參數的widget（右）

    主要功能： 當作__img_edit__和__control__間溝通的橋梁，如果有功能會同時用到這兩個widget，則會在MainFrame實作
    """
    __img_edit__: ImageEditWindow # 圖片顯示視窗
    __control__: ControlFrame     # 控制面版

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
            , filedialog.askopenfilename(filetypes=[("img", ["*.jpg", "*.png", "*.tif"])], initialdir="./workspace/")
        )
        self.__img_edit__.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        # 狀態欄
        ttk.Label(self, textvariable=self.__img_edit__.WINDOW_MESSAGE).grid(row=1, column=0, columnspan=2, sticky=tk.NW)

        # 控制面版
        self.__control__ = ControlFrame(self)
        self.__control__.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 載入設定檔
        self.__read_setting__()

    def __read_setting__(self):
        try:
            f = open("./workspace/setting.json", "rt")
            content = json.load(f)
            f.close()

            if "WHEEL_SENSITIVITY" in content.keys():
                self.__img_edit__.WHEEL_SENSITIVITY = content["WHEEL_SENSITIVITY"]
            if "MOUSE_SENSITIVITY" in content.keys():
                self.__img_edit__.MOUSE_SENSITIVITY = content["MOUSE_SENSITIVITY"]
            if "label" in content.keys():
                self.__control__.LABEL_COMBO.configure(values=content['label'])
                self.__control__.LABEL_COMBO.set(content['label'][0])

        except OSError:
            messagebox.showwarning("setting.json not found", "無法載入./workspace/setting.json")

    pass # end of class MainFrame

def main():
    root = tk.Tk()

    mainframe = MainFrame(root)
    mainframe.pack(expand=True, fill=tk.BOTH)

    root.geometry("=1000x600+20+20")
    root.mainloop()

if __name__ == "__main__":
    main()
