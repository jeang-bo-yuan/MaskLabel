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