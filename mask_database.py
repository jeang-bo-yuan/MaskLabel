import cv2
import numpy as np
from tkinter import messagebox
import os.path
import json

class MaskDatabase:
    """
    用來存放所有已加入的mask
    """
    __database__: list[dict] # 每一個mask都以一個dict表示，其格式為 { "bbox": [x1, y1, x2, y2], "label": "標籤", "Mask": 二維的int陣列 }
    __hilight_idx__: int     # 將要突顯的 mask 的 index 給快取起來
    __hilight_cnt__: cv2.Mat | None # 將要突顯的 mask 的 contour 給快取起來

    def __init__(self):
        """
        初始化
        """
        self.__database__ = list()
        self.__hilight_idx__ = -1
        self.__hilight_cnt__ = None

    def append(self, bbox: tuple[int], label: str, mask: list[list[int]]):
        """
        新增一個mask進database
        """
        self.__database__.append({ "bbox": bbox, "label": label, "Mask": mask })

    def delete(self, idx: int):
        """
        刪掉第idx個mask

        Args:
            idx: index，0 -> 第一個
        """
        # 刪掉第idx個
        # https://stackoverflow.com/a/627453/20876404
        del self.__database__[idx]

    def query(self, idx: int):
        """
        查找database中第idx個

        Args:
            idx: 第幾項，從0開始算起
        """
        return self.__database__[idx]

    # 繪製 ##################################################################################################################

    def set_highlight(self, idx: int):
        """
        下次render時，將第idx個mask的區域給著色

        Aegs:
            idx: 要突顯的 mask 的 index，若超出範圍則不著色
        """
        # check if in range
        if idx in range(len(self.__database__)):
            # already in the cache
            if idx == self.__hilight_idx__:
                return
            else:
                x, y = self.__database__[idx]["bbox"][0:2]
                img = np.array(self.__database__[idx]["Mask"], dtype=np.uint8)

                self.__hilight_idx__ = idx
                self.__hilight_cnt__ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0][0]
                self.__hilight_cnt__[:, :, 0] += x
                self.__hilight_cnt__[:, :, 1] += y
        else:
            self.__hilight_idx__ = -1
            self.__hilight_cnt__ = None

    def render(self, img: cv2.Mat, bbox: tuple[int]):
        """
        將database中所有mask的bounding box畫出來

        Args:
            img: 要畫在哪個圖片上
            bbox: img在原圖中的位置(x, y, w, h)
        """
        x, y = bbox[0:2]

        # 對於每個mask
        for mask_data in self.__database__:
            # 取出mask的bounding box
            x1, y1, x2, y2 = mask_data['bbox']

            # 繪製時要將座標轉成相對於可視範圍的左上角
            # 因為mask是位在 x 屬於 [x1, x2) 且 y 屬於 [y1, y2) 的區域，所以右下角的座標要減一
            cv2.rectangle(img, (x1 - x, y1 - y), (x2 - x - 1, y2 - y - 1), (191, 93, 2))

        if self.__hilight_cnt__ is not None:
            # 將圖片複製一份
            img_cpy = img.copy()

            # 繪製contour包住的區塊
            cnt = self.__hilight_cnt__.copy()
            cnt[:, :, 0] -= x    # 移動，使之相對於圖片左上角
            cnt[:, :, 1] -= y
            cv2.fillPoly(img_cpy, [cnt], (255, 0, 0))

            # 將兩張圖疊加
            cv2.addWeighted(img, 0.5, img_cpy, 0.5, 0, dst=img)

    # 存讀檔 ####################################################################################################

    def load_json(self, img_path: str):
        """
        讀取json檔中的內容，並將其存進__database__。
        嘗試讀取`{img_path}.json`並進行初始化。若該json不存在或不合格式則將__database__清空。

        Args:
            img_path: 圖檔的路徑，路徑的basename要是圖檔的檔名
        """
        JSON_PATH = f'{img_path}.json'
        basename = os.path.basename(img_path)

        if not os.path.exists(JSON_PATH):
            messagebox.showinfo("File Not Found", f'{JSON_PATH} 不存在，一切將從零開始')
            self.__database__.clear()
            return
        
        try:
            with open(JSON_PATH, 'rt') as f:
                content = json.load(f)
                assert basename in content.keys(), f'{JSON_PATH} 沒有包含 "{basename}" 這個key'
                
                mask_data = content[basename]

                for k in mask_data.keys():
                    assert 'bbox' in mask_data[k],                        f'{JSON_PATH} 中的 "{basename}"/"{k}"         沒有 "bbox" 這個key'
                    assert type(mask_data[k]['bbox']) == list,            f'{JSON_PATH} 中的 "{basename}"/"{k}"/"bbox"  應該要是整數列表'
                    assert len(mask_data[k]['bbox']) == 4,                f'{JSON_PATH} 中的 "{basename}"/"{k}"/"bbox"  應該要是長度4'
                    assert 'label' in mask_data[k],                       f'{JSON_PATH} 中的 "{basename}"/"{k}"         沒有 "label" 這個key'
                    assert type(mask_data[k]['label']) == str,            f'{JSON_PATH} 中的 "{basename}"/"{k}"/"label" 應該要是字串'
                    assert 'Mask' in mask_data[k],                        f'{JSON_PATH} 中的 "{basename}"/"{k}"         沒有 "Mask" 這個key'
                    assert type(mask_data[k]['Mask']) == list,            f'{JSON_PATH} 中的 "{basename}"/"{k}"/"Mask"  應該要是整數二維陣列'

                    self.__database__.append({
                        'bbox': mask_data[k]['bbox'], 'label': mask_data[k]['label'], 'Mask': mask_data[k]['Mask']
                    })

        except Exception as e:
            messagebox.showerror("Invalid", f'{repr(e)}。\n{JSON_PATH} 不合格式，即將清空所有遮罩')
            self.__database__.clear()
            return
        
        messagebox.showinfo("Loading Succeeds", f'成功載入 {JSON_PATH}')
        
    def write_json(self, img_path: str):
        """
        將__database__輸出到 `{img_path}.json`，輸出格式：
        ```
        {
            img_file_name: {
                "0": {"bbox": ..., "label": ..., "Mask": ...},
                "1": {"bbox": ..., "label": ..., "Mask": ...},
                "2": {"bbox": ..., "label": ..., "Mask": ...},
                ...
                "N": {"bbox": ..., "label": ..., "Mask": ...}
            }
        }
        ```

        Args:
            img_path: 圖片的路徑，路徑的basename要是圖檔的檔名
        """
        JSON_PATH = f'{img_path}.json'
        basename = os.path.basename(img_path)

        if not messagebox.askyesno("Save", f'是否要將標記的結果存進 {JSON_PATH} ?'):
            return
        
        try:
            with open(JSON_PATH, 'wt') as f:
                out_data = { basename: dict() }

                for i, v in enumerate(self.__database__):
                    out_data[basename][i] = v

                f.write(json.dumps(out_data, indent=4, ensure_ascii=True))
        except Exception as e:
            messagebox.showerror("Save Fail", f'儲存失敗，原因\nrepr(e)')
        else:
            messagebox.showinfo("Saving Succeeds", "儲存成功")