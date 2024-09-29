import json
import numpy as np
import cv2
import os.path
import sys

def convert_mask(JSON_PATH: str, MASK_TRUE: int):
    """
    將 JSON_PATH 這個json檔中的'Mask'的最大值轉成 MASK_TRUE

    Args:
        JSON_PATH: json檔在哪
        MASK_TRUE: 如果Mask匹配的話應該換成哪個值
    """
    with open(JSON_PATH, 'rt') as f:
        content = json.load(f)

    # 對於每個圖
    for img in content.keys():
        # 對於每個數字
        for num in content[img].keys():
            # 取出Mask
            mask = np.array(content[img][num]['Mask'], dtype=np.uint8)
            # 將大於0的換成 MASK_TRUE
            cv2.threshold(mask, 0, float(MASK_TRUE), cv2.THRESH_BINARY, dst=mask)
            # write back
            content[img][num]['Mask'] = mask.tolist()
    
    dirname, filename = os.path.split(JSON_PATH)
    outfile = os.path.join(dirname, f'mask{MASK_TRUE}_{filename}')

    print(f'寫入 {outfile} 中......')

    with open(outfile, 'wt') as f:
        json.dump(content, f)
    


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用這個工具來將標記結果中的Mask轉成不同數字\n（預設情況下，「匹配」是255，你可以用這個工具把它調成1）")
        print("示例")
        print("\tconvert_mask.py <input.json> <新的Mask值>")
        sys.exit(0)

    convert_mask(sys.argv[1], sys.argv[2])