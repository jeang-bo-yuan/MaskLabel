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

        # 綁定事件
        self.bind("<Configure>", self.update) # 調整大小


    def update(self, event : tk.Event):
        """
        更新顯示的圖片
        """
        # 調整圖片大小
        img = cv2.resize(self.ORIGINAL_IMG, (event.width, event.height))
        img = PIL.Image.fromarray(img)
        img = PIL.ImageTk.PhotoImage(img)

        # 設置圖片
        self["image"] = img
        self.__SHOWED_IMG__ = img # 增加reference，以免img被回收
    