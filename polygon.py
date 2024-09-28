import cv2
import numpy as np

class Polygon:
    """
    在視窗上可供編輯的多邊形
    """
    __points__: list[list[int]]    # n * 2的陣列，每一列包含一個點 (x, y)

    def __init__(self):
        """
        初始化
        """
        self.__points__ = list()

    def addPoint(self, x: int, y: int):
        """
        新增一個點
        """
        self.__points__.append([x, y])

    def popPoint(self):
        """
        刪掉最後加入的一個點
        """
        if len(self.__points__) != 0:
            self.__points__.pop()

    def clear(self):
        """
        清空
        """
        self.__points__.clear()

    def render(self, img: cv2.Mat, bbox: tuple[int], close: bool):
        """
        將所有點畫到img上

        Args:
            img: 繪製的圖片
            bbox: bounding box (x, y, w, h)
            close: 是否繪製封閉曲線
        """
        pts = np.array(self.__points__, dtype=np.int32)
        pts = pts.reshape((-1, 1, 2))  # 調成 n * 1 * 2

        pts[:, :, 0] -= bbox[0]   # 移動，使每一個點的座標變成相對於bbox的左上角
        pts[:, :, 1] -= bbox[1]

        cv2.polylines(img, [pts], close, (0, 0, 255), 1)

        for i in range(pts.shape[0]):
            cv2.circle(img, pts[i, 0], 3, (255, 0, 0))