import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
from typing import Callable
import cv2
import numpy as np
import PIL.Image
import PIL.ImageTk

class ImageEditWindow(ttk.Label):
    """
    用來顯示及編輯圖片的視窗

    功能：
    - 顯示
    - Zoom In／Zoom Out（滑鼠滾輪）
    - 拖動顯示範圍（按住滑鼠右鍵）

    為了保持該widget的泛用性，我希望只保留上面3個基礎的功能，即檢視圖片的功能。
    其他進階功能則要自己擴充，可能的擴充方向：
    1. 將 WINDOW_MESSAGE 綁定到外部的Label上
    2. 設置 render_callback ，這樣更新畫面時可以用自定的callback來繪製其他內容
    3. 綁定按鍵事件到外部的函式上
    """
    WHEEL_SENSITIVITY: float  = -0.05   # 滑鼠滾輪的靈敏度
    MOUSE_SENSITIVITY: float  = 1       # 滑鼠平移的靈敏度
    ORIGINAL_IMG: cv2.Mat               # 原始圖片
    FILE_PATH: str                      # 圖檔路徑
    WINDOW_MESSAGE: tk.StringVar        # 欲顯示的資訊（含鼠標位置、viewport）
    __viewport__: list[int]             # 顯示範圍，[x, y, dx, dy]，分別代表 [起始x座標, 起始y座標, 水平長度, 垂直長度]，意義跟 cv2.boundingRect 的回傳值一樣
    __ratio__: int                      # 縮放比例，1->最小，100->最大
    __drag_start__: list[int]           # 開始拖移的位置，相對於widget左上角的（x, y）座標
    __render_callback__: Callable[[cv2.Mat, tuple[int]], None] | None # 繪製額外資訊的callback，參數有兩個：切割後的圖片、在原圖片中的bounding box (x, y, w, h)
    __SHOWED_IMG__: PIL.ImageTk.PhotoImage


    def __init__(self, master: tk.Misc, file_path: str, render_callback: Callable[[cv2.Mat, tuple[int]], None] | None = None):
        """
        初始化一個畫面編輯視窗

        Args:
            master: 屬於哪個Widget
            file_path: 圖片的路徑
            render_callback: 用來繪製額外資訊的callback，參數有兩個：切割後的圖片、在原圖片中的bounding box (x, y, w, h)
        """
        ttk.Label.__init__(self, master, text="", anchor=tk.NW)

        # 原圖片
        # 解決「當路徑中有Unicode字元時」造成cv2.imread失敗的問題
        # https://jdhao.github.io/2019/09/11/opencv_unicode_image_path/#google_vignette
        try:
            self.ORIGINAL_IMG = cv2.imdecode(np.fromfile(file_path), cv2.IMREAD_COLOR)
        except FileNotFoundError:
            messagebox.showerror("Error", f"無法開啟圖片 \"{file_path}\"")
            sys.exit(-1)
        # 圖片路徑
        self.FILE_PATH = file_path
        # 顯示資訊
        self.WINDOW_MESSAGE = tk.StringVar(value=f'載入 {file_path} 成功')
        # 顯示的圖片範圍
        self.__viewport__ = [0, 0, self.ORIGINAL_IMG.shape[1], self.ORIGINAL_IMG.shape[0]]
        # 縮放比例
        self.__ratio__ = 100
        # render callback
        self.__render_callback__ = render_callback

        # 綁定事件
        self.bind("<Button-3>", self.set_drag_start) # 按下滑鼠右鍵時計下位置
        self.bind("<B3-Motion>", self.pan)    # 按住滑鼠右鍵時可以平移viewport
        self.bind("<MouseWheel>", self.zoom)  # zoom in / zoom out
        self.bind("<Configure>", self.update) # 調整大小
        self.bind("<Motion>", self.update_message) # 每當滑鼠移動，更新位置資訊


    def set_drag_start(self, event : tk.Event):
        """
        將 `event.x` 和 `event.y` 記錄在 `self.__drag_start__`

        Args:
            event: tkinter的Event物件
        """
        self.__drag_start__ = [event.x, event.y]


    def pan(self, event : tk.Event):
        """
        平移viewport

        Args:
            event: tkinter的Event物件，用來知道滑鼠的位置
        """
        # 依據滑鼠移動的距離計算dx, dy
        dx = int((self.__drag_start__[0] - event.x) * self.MOUSE_SENSITIVITY)
        dy = int((self.__drag_start__[1] - event.y) * self.MOUSE_SENSITIVITY)

        # 移動viewport
        self.__viewport__[0] += dx
        self.__viewport__[1] += dy

        # 將現在的位置記下，這樣下次觸發 <B3-Motion> 時才能知道又移動了多少
        self.set_drag_start(event)
        # 更新畫面
        self.__adjust_viewport__()
        self.update(None)

    def zoom(self, event : tk.Event):
        """
        當滾動滑鼠時zoom in/ zoom out

        Args:
            event: tkinter的Event物件，用來知道滑鼠的位置
        """
        pixelX, pixelY = self.to_original_pixel(event.x, event.y)
        old_x, old_y, old_dx, old_dy = self.__viewport__

        # 依滾動量，更新ratio
        delta = int(event.delta * self.WHEEL_SENSITIVITY)
        self.__ratio__ = np.clip(self.__ratio__ + delta, 1, 100)

        # 改變viewport的尺寸
        new_dx = self.ORIGINAL_IMG.shape[1] * self.__ratio__ // 100  # 尺寸是以原圖的 ratio% 計算
        new_dy = self.ORIGINAL_IMG.shape[0] * self.__ratio__ // 100
        self.__viewport__[2:] = [new_dx, new_dy]

        # 移動viewport，使得(pixelX, pixelY)在移動後的viewport中仍有一樣的相對位置
        #
        # (pixelX - x) / dx = (pixelX - x') / dx'
        # 移項得 x' = pixelX - (pixelX - x) * dx' / dx
        #
        self.__viewport__[0] = pixelX - (pixelX - old_x) * new_dx // old_dx
        #
        # (pixelY - y) / dy = (pixelY - y') / dy'
        # 移項得 y' = pixelY - (pixelY - y) * dy' / dy
        #
        self.__viewport__[1] = pixelY - (pixelY - old_y) * new_dy // old_dy

        # update
        self.__adjust_viewport__()
        self.update(None)


    def update(self, event : tk.Event | None):
        """
        更新顯示的圖片

        Args:
            event: 用不到，但為了將update傳進bind，所以還是留著
        """
        # 切割圖片
        x, y, dx, dy = self.__viewport__
        img = self.ORIGINAL_IMG[y : y+dy, x : x+dx].copy()

        # 呼叫 render callback
        if self.__render_callback__ is not None:
            self.__render_callback__(img, self.__viewport__)

        # 調整圖片大小
        img = cv2.resize(img, (self.winfo_width(), self.winfo_height()))
        img = PIL.Image.fromarray(img)
        img = PIL.ImageTk.PhotoImage(img)

        # 設置圖片
        self["image"] = img
        self.__SHOWED_IMG__ = img # 增加reference，以免img被回收

    
    def update_message(self, event : tk.Event):
        """
        移據滑鼠現在的位置更新顯示的資訊

        Args:
            event: 用來取得滑鼠的位置
        """
        pixelX, pixelY = self.to_original_pixel(event.x, event.y)
        self.WINDOW_MESSAGE.set(f"x: {pixelX}, y: {pixelY}, viewport: {self.__viewport__}")

    
    def to_original_pixel(self, x : int, y : int) -> tuple[int, int]:
        """
        在widget中的(x, y)對應到原圖中的哪個像素

        Args:
            x: 離widget的左邊界幾個像素。範圍：[0, self.winfo_width())
            y: 離widget的上邊界幾個像素。範圍：[0, self.winfo_height())

        Return:
            (pixelX, pixelY): (x, y)對應到原圖中的 `self.ORIGINAL_IMG[pixelY][pixelX]`
        """
        viewX, viewY, dx, dy = self.__viewport__

        pixelX = int(np.interp(x, [0, self.winfo_width()], [viewX, viewX + dx]))
        pixelY = int(np.interp(y, [0, self.winfo_height()], [viewY, viewY + dy]))
        
        return (pixelX, pixelY)
    

    def __adjust_viewport__(self):
        """
        調整viewport，避免移出圖片範圍
        """
        x, y, dx, dy = self.__viewport__

        x = np.clip(x, 0, self.ORIGINAL_IMG.shape[1] - dx)
        y = np.clip(y, 0, self.ORIGINAL_IMG.shape[0] - dy)

        self.__viewport__[0:2] = [x, y]

    pass # end of ImageEditWindow
