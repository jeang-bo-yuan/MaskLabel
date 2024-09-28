import cv2

class MaskDatabase:
    """
    用來存放所有已加入的mask
    """
    __database__: list[dict] # 每一個mask都以一個dict表示，其格式為 { "bbox": [x1, y1, x2, y2], "label": "標籤", "Mask": 二維的int陣列 }

    def __init__(self):
        self.__database__ = list()

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

            # 繪製是要將座標轉成相對於可視範圍的左上角
            cv2.rectangle(img, (x1 - x, y1 - y), (x2 - x, y2 - y), (191, 93, 2))