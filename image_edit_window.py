import tkinter as tk
from tkinter import ttk
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
    """
    WHEEL_SENSITIVITY: float  = -0.05 # 滑鼠滾輪的靈敏度
    MOUSE_SENSITIVITY: float  = 1 # 滑鼠平移的靈敏度
    ORIGINAL_IMG: cv2.Mat   # 原始圖片
    FILE_PATH: str          # 圖檔路徑
    __viewport__: list[int] # 顯示範圍，[x, y, dx, dy]，分別代表 [起始x座標, 起始y座標, 水平長度, 垂直長度]，意義跟 cv2.boundingRect 的回傳值一樣
    __ratio__: int          # 縮放比例，1->最小，100->最大
    __drag_start__: list[int] # 開始拖移的位置，相對於widget左上角的（x, y）座標
    __SHOWED_IMG__: PIL.ImageTk.PhotoImage


    def __init__(self, master: tk.Misc, file_path: str):
        """
        初始化一個畫面編輯視窗

        Args:
            master: 屬於哪個Widget
            file_path: 圖片的路徑
        """
        ttk.Label.__init__(self, master, text="", anchor=tk.NW)

        # 原圖片
        # 解決「當路徑中有Unicode字元時」造成cv2.imread失敗的問題
        # https://jdhao.github.io/2019/09/11/opencv_unicode_image_path/#google_vignette
        self.ORIGINAL_IMG = cv2.imdecode(np.fromfile(file_path), cv2.IMREAD_COLOR)
        # 圖片路徑
        self.FILE_PATH = file_path
        # 顯示的圖片範圍
        self.__viewport__ = [0, 0, self.ORIGINAL_IMG.shape[1], self.ORIGINAL_IMG.shape[0]]
        # 縮放比例
        self.__ratio__ = 100

        # 綁定事件
        self.bind("<Button-3>", self.set_drag_start) # 按下滑鼠右鍵時計下位置
        self.bind("<B3-Motion>", self.pan)    # 按住滑鼠右鍵時可以平移viewport
        self.bind("<MouseWheel>", self.zoom)  # zoom in / zoom out
        self.bind("<Configure>", self.update) # 調整大小


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
        pixelX, pixelY = self.__to_original_pixel__(event.x, event.y)
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
        img = self.ORIGINAL_IMG[y : y+dy, x : x+dx]

        # 調整圖片大小
        # 為什麼tkinter中的width是直的方向（？？？
        img = cv2.resize(img, (self.winfo_width(), self.winfo_height()))
        img = PIL.Image.fromarray(img)
        img = PIL.ImageTk.PhotoImage(img)

        # 設置圖片
        self["image"] = img
        self.__SHOWED_IMG__ = img # 增加reference，以免img被回收

    
    def __to_original_pixel__(self, x : int, y : int) -> tuple[int, int]:
        """
        在widget中的(x, y)對應到原圖中的哪個像素

        Args:
            x: 離widget的左邊界幾個像素
            y: 離widget的上邊界幾個像素

        Return:
            (pixelX, pixelY): (x, y)對應到原圖中的 `self.ORIGINAL_IMG[pixelY][pixelX]`
        """
        viewX, viewY, dx, dy = self.__viewport__
        IMG_ROW, IMG_COL, _ = self.ORIGINAL_IMG.shape

        # 為什麼tkinter中的height是橫的方向（？？？
        pixelX = int(np.interp(x, [0, self.winfo_height()], [viewX, viewX + dx]))
        pixelY = int(np.interp(y, [0, self.winfo_width()], [viewY, viewY + dy]))
        
        # 避免x, y出現在邊界而導致pixelX, pixelY超出邊界
        return np.clip((pixelX, pixelY), [0, 0], [IMG_COL - 1, IMG_ROW - 1])
    

    def __adjust_viewport__(self):
        """
        調整viewport，避免移出圖片範圍
        """
        x, y, dx, dy = self.__viewport__

        x = np.clip(x, 0, self.ORIGINAL_IMG.shape[1] - dx)
        y = np.clip(y, 0, self.ORIGINAL_IMG.shape[0] - dy)

        self.__viewport__[0:2] = [x, y]
    