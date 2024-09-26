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
    - 拖動顯示範圍（按住滑鼠中鍵）
    - 點擊畫面以新增mask的邊界點（滑鼠左鍵）
    """
    WHEEL_SENSITIVITY: int  = 0.05 # 滑鼠滾輪的靈敏度
    ORIGINAL_IMG: cv2.Mat   # 原始圖片
    FILE_PATH: str          # 圖檔路徑
    __viewport__: list[int] # 顯示範圍，[r, c, dr, dc]，分別代表 [起始列, 起始欄, 幾列, 幾欄]
    __ratio__: int          # 縮放比例，1->最小，100->最大
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
        self.__viewport__ = [0, 0, self.ORIGINAL_IMG.shape[0], self.ORIGINAL_IMG.shape[1]]
        # 縮放比例
        self.__ratio__ = 100

        # 綁定事件
        self.bind("<MouseWheel>", self.zoom)  # zoom in / zoom out
        self.bind("<Configure>", self.update) # 調整大小


    def zoom(self, event : tk.Event):
        """
        當滾動滑鼠時zoom in/ zoom out
        """
        pixelX, pixelY = self.__to_original_pixel__(event.x, event.y)
        old_r, old_c, old_dr, old_dc = self.__viewport__

        # 依滾動量，更新ratio
        delta = int(event.delta * self.WHEEL_SENSITIVITY)
        self.__ratio__ = np.clip(self.__ratio__ + delta, 1, 100)

        # 改變viewport的尺寸
        new_dr = self.ORIGINAL_IMG.shape[0] * self.__ratio__ // 100  # 尺寸是以原圖的 ratio% 計算
        new_dc = self.ORIGINAL_IMG.shape[1] * self.__ratio__ // 100
        self.__viewport__[2:] = [new_dr, new_dc]

        # 移動viewport，使得(pixelX, pixelY)在移動後的viewport中仍有一樣的相對位置
        # (pixelY - r) / dr = (pixelY - r') / dr'
        self.__viewport__[0] = pixelY - (pixelY - old_r) * new_dr // old_dr
        # (pixelX - c) / dc = (pixelX - c') / dc'
        self.__viewport__[1] = pixelX - (pixelX - old_c) * new_dc // old_dc

        # update
        self.__adjust_viewport__()
        self.update(None)


    def update(self, event : tk.Event | None):
        """
        更新顯示的圖片
        """
        # 切割圖片
        r, c, dr, dc = self.__viewport__
        img = self.ORIGINAL_IMG[r : r+dr, c : c+dc]

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
        r, c, dr, dc = self.__viewport__
        IMG_ROW, IMG_COL, _ = self.ORIGINAL_IMG.shape

        # 為什麼tkinter中的height是橫的方向（？？？
        pixelX = int(np.interp(x, [0, self.winfo_height()], [c, c + dc]))
        pixelY = int(np.interp(y, [0, self.winfo_width()], [r, r + dr]))
        
        # 避免x, y出現在邊界而導到pixelX, pixelY超出邊界
        return np.clip((pixelX, pixelY), [0, 0], [IMG_COL - 1, IMG_ROW - 1])
    

    def __adjust_viewport__(self):
        """
        調整viewport，避免移出圖片範圍
        """
        r, c, dr, dc = self.__viewport__

        r = np.clip(r, 0, self.ORIGINAL_IMG.shape[0] - dr)
        c = np.clip(c, 0, self.ORIGINAL_IMG.shape[1] - dc)

        self.__viewport__[0:2] = [r, c]
    