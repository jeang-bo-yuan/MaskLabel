import os.path
import json
import sys

def split_json(JSON_PATH: str):
    # 將JSON檔打開，並解析
    with open(JSON_PATH, 'rt') as f:
        content = json.load(f)

    # 看JSON檔在哪，這個目錄是要輸出的位置
    dirname = os.path.dirname(JSON_PATH)

    # 對於每一個key，將key和其內容輸出到 {key}.json
    for key in content.keys():
        out = { key: content[key] }
        outfile_path = os.path.join(dirname, f'{key}.json')

        print(f'寫入 "{outfile_path}" 中......')

        with open(outfile_path, 'wt') as outfile:
            json.dump(out, outfile, indent=4)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("這程式可以用來將json檔中的內容進行分割。分割的方式：將json中最上層的每個key分出來，放在一個獨立的檔案。")
        print("示例")
        print("\tpython split_json.py foo1.json [foo2.json [foo3.json ...]]")
        sys.exit(0)
    
    for i in range(1, len(sys.argv)):
        split_json(sys.argv[i])