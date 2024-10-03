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

    # 繪製 #################################################################################################################

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

        x, y, w, h = bbox
        thick = int(np.max((w * 0.001, h * 0.001, 1)))

        pts[:, :, 0] -= x   # 移動，使每一個點的座標變成相對於bbox的左上角
        pts[:, :, 1] -= y

        cv2.polylines(img, [pts], close, (0, 0, 255), thick, cv2.LINE_AA)

        for i in range(pts.shape[0]):
            cv2.circle(img, pts[i, 0], thick * 3, (255, 0, 0), thick)

    # 轉換成輸出格式 ########################################################################################################

    def toMask(self) -> tuple[tuple[int], cv2.Mat] | tuple[None, None]:
        """
        將多邊形包住的範圍變成mask，並計算bbox

        Return:
            (bbox, mask_img): bbox是(x1, y1, x2, y2)，而mask_img是一張黑白圖片（shape = H * W）白色為遮罩，
                              如果polygon沒有3個點則回傳None
        """
        if len(self.__points__) < 3:
            return None, None

        pts = np.array(self.__points__, dtype=np.int32)
        pts = pts.reshape((-1, 1, 2))

        x, y, w, h = cv2.boundingRect(pts)

        pts[:, :, 0] -= x  # 移動每個點，使其相對於bbox的左上角
        pts[:, :, 1] -= y

        img = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(img, [pts], (255), cv2.LINE_4)

        return (x, y, x + w, y + h), img

        
