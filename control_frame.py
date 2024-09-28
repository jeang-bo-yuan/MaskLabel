import tkinter as tk
from tkinter import ttk

class ControlFrame(ttk.Frame):
    """
    控制面版

    功能： 定義互動介面
    """
    LABEL_COMBO: ttk.Combobox          # 包含所有從setting.json讀入的label
    CLEAR_BTN: ttk.Button              # 清空所有邊界點
    DELETE_BTN: ttk.Button             # 刪掉最後一個邊界點
    SHOULD_CLOSE: tk.StringVar         # 繪製邊界時是否要頭尾相連
    ADD_MASK_BTN: ttk.Button           # 將邊界內的範圍轉成Mask，並加入MASK_LIST
    DEL_MASK_BTN: ttk.Button           # 刪除MASK_LIST中選定的mask
    SHOULD_DRAW_MASK_BOX: tk.StringVar # 是否將MASK_LIST中所有MASK的bounding box畫出來
    MASK_LIST: tk.Listbox              # 顯示所有的mask

    def __init__(self, master : tk.Misc):
        """
        初始化控制面版
        
        Args:
            master: parent widget
        """
        ttk.Frame.__init__(self, master, padding=(10, 0, 10, 0))
        self.rowconfigure((1, 4, 5), minsize=30)
        self.rowconfigure(7, weight=1)
        
        # 標籤
        ttk.Label(self, text="標籤").grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.LABEL_COMBO = ttk.Combobox(self, state="readonly")
        self.LABEL_COMBO.grid(row=0, column=1, sticky=(tk.W, tk.E), columnspan=3)

        ttk.Separator(self).grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))

        # 按鈕
        self.CLEAR_BTN = ttk.Button(self, text="清除所有點")
        self.CLEAR_BTN.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.DELETE_BTN = ttk.Button(self, text="刪除最新加入的點")
        self.DELETE_BTN.grid(row=2, column=2, columnspan=2, sticky=(tk.W, tk.E))
        # Check Box
        self.SHOULD_CLOSE = tk.StringVar(value="0")
        ttk.Checkbutton(self, text="繪製封閉的邊界", variable=self.SHOULD_CLOSE).grid(row=3, column=0, columnspan=4, sticky=tk.W)

        ttk.Separator(self).grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))

        # Mask
        self.ADD_MASK_BTN = ttk.Button(self, text="加入Mask")
        self.ADD_MASK_BTN.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.DEL_MASK_BTN = ttk.Button(self, text="刪除Mask")
        self.DEL_MASK_BTN.grid(row=5, column=2, columnspan=2, sticky=(tk.W, tk.E))

        self.SHOULD_DRAW_MASK_BOX = tk.StringVar(value='1')
        ttk.Checkbutton(self, text="繪製Mask的Bounding Box", variable=self.SHOULD_DRAW_MASK_BOX).grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E))

        # Mask 列表
        scroll = ttk.Scrollbar(self, orient='vertical')
        self.MASK_LIST = tk.Listbox(self, selectmode="single", yscrollcommand=scroll.set)
        self.MASK_LIST.grid(row=7, column=0, columnspan=3, sticky=(tk.N, tk.S, tk.E, tk.W))
        scroll.configure(command=self.MASK_LIST.yview)
        scroll.grid(row=7, column=3, sticky=(tk.N, tk.S))

        # 事件綁定
        self.SHOULD_CLOSE.trace_add(mode="write", callback=self.__send_repaint__)
        self.SHOULD_DRAW_MASK_BOX.trace_add(mode='write', callback=self.__send_repaint__)


    def __send_repaint__(self, *args):
        """
        送出 <<Repaint>> virtual event，MainFrame應該將這事件綁定到 ImageEditWindow 的 update

        Args:
            args: trace_add 的 callback 需要傳3個str，但我用不到
        """
        self.event_generate("<<Repaint>>")

    def reset_mask_list(self, database: list[dict]):
        """
        重設MASK_LIST中的內容

        Args:
            database: 包含所有的mask，每個mask都是一個dict，{'bbox': ..., 'label': ..., 'Mask': ...}
        """
        # 刪掉全部
        self.MASK_LIST.delete(0, tk.END)

        # 將database的內容塞入MASK_LIST
        for mask_data in database:
            self.MASK_LIST.insert(tk.END, mask_data['label'])

    pass # end of ControlFrame
