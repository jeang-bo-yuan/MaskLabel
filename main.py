from image_edit_window import ImageEditWindow
from control_frame import ControlFrame
from polygon import Polygon
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import json
import cv2

class MainFrame(ttk.Frame):
    """
    主要的視窗，包含圖片顯示的widget（左）和設定參數的widget（右）

    主要功能： 當作__img_edit__和__control__間溝通的橋梁，如果有功能會同時用到這兩個widget，則會在MainFrame實作
    """
    __img_edit__: ImageEditWindow # 圖片顯示視窗
    __control__: ControlFrame     # 控制面版
    __polygon__: Polygon          # 多邊形

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
            , file_path= filedialog.askopenfilename(filetypes=[("img", ["*.jpg", "*.png", "*.tif"])], initialdir="./workspace/")
            , render_callback= self.__render_polygon_and_box__
        )
        self.__img_edit__.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        # 狀態欄
        ttk.Label(self, textvariable=self.__img_edit__.WINDOW_MESSAGE).grid(row=1, column=0, columnspan=2, sticky=tk.NW)

        # 控制面版
        self.__control__ = ControlFrame(self)
        self.__control__.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 多邊形
        self.__polygon__ = Polygon()

        # 載入設定檔
        self.__read_setting__()

        # 事件綁定
        self.__img_edit__.bind("<Button-1>", self.__add_polygon_point__) # 按下左鍵，則新增一點
        self.__control__.bind("<<Repaint>>", self.__img_edit__.update)   # 收到repaint後更新畫面
        self.__control__.DELETE_BTN.configure(command=self.__delete_last_polygon_point__)
        self.__control__.CLEAR_BTN.configure(command=self.__clear_polygon_point__)

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

    def __add_polygon_point__(self, event: tk.Event):
        """
        在polygon中新增一點

        Args:
            event: 用來取得滑鼠的x, y
        """
        # 將滑鼠指到的像素點加入polygon
        pixelX, pixelY = self.__img_edit__.to_original_pixel(event.x, event.y)
        self.__polygon__.addPoint(pixelX, pixelY)

        # 更新畫面
        self.__img_edit__.update(None)

    def __delete_last_polygon_point__(self, event = None):
        """
        刪掉最後一點
        """
        self.__polygon__.popPoint()
        self.__img_edit__.update(None)

    def __clear_polygon_point__(self):
        """
        清除polygon中所有點
        """
        self.__polygon__.clear()
        self.__img_edit__.update(None)

    def __render_polygon_and_box__(self, img: cv2.Mat, bbox: tuple[int]):
        """
        將多邊形和Mask的bounding box畫出來，作為ImageEditWindow的render callback

        Args:
            img: 圖片
            bbox: (x, y, w, h)
        """
        close = self.__control__.SHOULD_CLOSE.get() == '1'
        self.__polygon__.render(img, bbox, close)

    pass # end of class MainFrame

def main():
    root = tk.Tk()

    def setup_mainFrame():
        btn.destroy()
        mainframe = MainFrame(root)
        mainframe.pack(expand=True, fill=tk.BOTH)

        # 按鍵要綁在 root，不然 mainFrame 的 focus 可能會被其他按鈕搶走
        root.bind("<Control-Key-z>", mainframe.__delete_last_polygon_point__)
        root.geometry("=1000x600+20+20")

    btn = ttk.Button(root, text="點我開始", command=setup_mainFrame)
    btn.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
