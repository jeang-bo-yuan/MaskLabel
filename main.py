from image_edit_window import ImageEditWindow
from control_frame import ControlFrame
from polygon import Polygon
from mask_database import MaskDatabase
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import json
import cv2
import numpy as np

class MainFrame(ttk.Frame):
    """
    主要的視窗，包含圖片顯示的widget（左）和設定參數的widget（右）

    主要功能： 當作__img_edit__和__control__間溝通的橋梁，如果有功能會同時用到這兩個widget，則會在MainFrame實作
    """
    __img_edit__: ImageEditWindow # 圖片顯示視窗
    __control__: ControlFrame     # 控制面版
    __polygon__: Polygon          # 多邊形
    __mask_db__: MaskDatabase     # 儲存所有的Mask

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
        # database
        self.__mask_db__ = MaskDatabase()
        self.reload_mask()

        # 載入設定檔
        self.__read_setting__()

        # 事件綁定
        self.__img_edit__.bind("<Button-1>", self.__add_polygon_point__) # 按下左鍵，則新增一點
        self.__control__.bind("<<Repaint>>", self.__img_edit__.update)   # 收到repaint後更新畫面
        self.__control__.DELETE_BTN.configure(command=self.__delete_last_polygon_point__)
        self.__control__.CLEAR_BTN.configure(command=self.__clear_polygon_point__)
        self.__control__.ADD_MASK_BTN.configure(command=self.__add_mask__)     # 按下按鈕->加入mask
        self.__control__.DEL_MASK_BTN.configure(command=self.__delete_mask__)  # 按下按鈕->移除mask
        self.__control__.MASK_LIST.bind("<Double-Button-1>", self.__focus_on_mask__)
        self.__control__.MASK_LIST.bind("f", self.__focus_on_mask__)
        self.__control__.MASK_LIST.bind("<KeyPress-Delete>", self.__delete_mask__)
        self.bind("<Destroy>", self.save_mask)

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

    def __add_mask__(self):
        """
        將__polygon__轉成遮罩，然後把它加入__mask_db__和MASK_LIST
        """
        bbox, img = self.__polygon__.toMask()
        if bbox is None:
            messagebox.showerror("Error", "至少需要3個點")
            return
        
        if cv2.getWindowProperty("mask", cv2.WND_PROP_VISIBLE):
            cv2.destroyWindow("mask")
        cv2.imshow("mask", img)

        label = self.__control__.LABEL_COMBO.get()
        # 在MASK_LIST中新增一個欄位，它的名字為「label」
        self.__control__.MASK_LIST.insert(tk.END, label)
        self.__control__.MASK_LIST.selection_clear(0, tk.END)
        self.__control__.MASK_LIST.selection_set(tk.END)
        # 加進database
        self.__mask_db__.append(bbox, label, img.tolist())

        # 如果有要繪製mask的bounding box，則要重新更新畫面
        if self.__control__.SHOULD_DRAW_MASK_BOX.get() == '1':
            self.__img_edit__.update(None)

    def __delete_mask__(self, event: tk.Event = None):
        """
        看MASK_LIST中哪個mask被選到就將它刪掉

        Args:
            event: 沒用到
        """
        # 所有選中的項目（型別為tuple）
        indices = self.__control__.MASK_LIST.curselection()
        if len(indices) == 0:
            return
        
        idx = indices[0]
        label = self.__control__.MASK_LIST.get(idx)

        if messagebox.askyesno("Delete", f"確定要刪掉 {label} (index={idx}) 嗎？"):
            # 從list刪掉
            self.__control__.MASK_LIST.delete(idx)
            # 從db刪掉
            self.__mask_db__.delete(idx)

        # 如果有要繪製mask的bounding box，則要重新更新畫面
        if self.__control__.SHOULD_DRAW_MASK_BOX.get() == '1':
            self.__img_edit__.update(None)
        
    def __focus_on_mask__(self, event: tk.Event):
        """ 
        將可視範圍聚焦在選定的mask上

        Args:
            event: 用不到，但為了傳給bind，所以還是留著
        """
        indicies = self.__control__.MASK_LIST.curselection()
        if len(indicies) == 0:
            return
        
        mask_data = self.__mask_db__.query(indicies[0])

        # 改viewport
        x1, y1, x2, y2 = mask_data['bbox']
        self.__img_edit__.change_viewport((x1, y1, x2 - x1, y2 - y1))

        # 顯示mask
        if cv2.getWindowProperty("mask", cv2.WND_PROP_VISIBLE):
            cv2.destroyWindow("mask")
        cv2.imshow("mask", np.array(mask_data['Mask'], dtype=np.uint8))


    def __render_polygon_and_box__(self, img: cv2.Mat, bbox: tuple[int]):
        """
        將多邊形和Mask的bounding box畫出來，作為ImageEditWindow的render callback

        Args:
            img: 圖片
            bbox: (x, y, w, h)
        """
        close = self.__control__.SHOULD_CLOSE.get() == '1'
        self.__polygon__.render(img, bbox, close)

        if self.__control__.SHOULD_DRAW_MASK_BOX.get() == '1':
            self.__mask_db__.render(img, bbox)

    def reload_mask(self, event: tk.Event = None):
        """
        重新載入 `./workspace/{img_file_name}.json`
        """
        self.__mask_db__.load_json(self.__img_edit__.FILE_NAME)
        self.__control__.reset_mask_list(self.__mask_db__.__database__)

    def save_mask(self, event: tk.Event = None):
        """
        將MASK_LIST中所有遮罩儲存下來
        """
        self.__mask_db__.write_json(self.__img_edit__.FILE_NAME)

    pass # end of class MainFrame

def main():
    root = tk.Tk()

    def setup_mainFrame():
        btn.destroy()
        mainframe = MainFrame(root)
        mainframe.pack(expand=True, fill=tk.BOTH)

        # 按鍵要綁在 root，不然 mainFrame 的 focus 可能會被其他按鈕搶走
        root.bind("<Control-Key-z>", mainframe.__delete_last_polygon_point__)
        root.bind("<Control-Key-s>", mainframe.save_mask)
        root.geometry("=1000x600+20+20")

    btn = ttk.Button(root, text="點我開始", command=setup_mainFrame)
    btn.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
