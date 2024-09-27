# About

在圖片上標識遮罩的工具，本工具可以在圖片上框出一個多邊形遮罩，並將其匯出。

匯出的資訊包含：
- 遮罩的bounding box
- 遮罩的label
- 代表遮罩的二維陣列

# Workflow

Step1. git clone後開啟本資料夾

Step2. 將要標記的圖片放在`workspace/`下

Step3. 執行`main.py`

# Setting JSON

`workspace/setting.json`是設定檔，格式如下：

```json
{
    "WHEEL_SENSITIVITY": "(float) Zoom In / Zoom Out的靈敏度",
    "MOUSE_SENSITIVITY": "(float) 拖動畫面的靈敏度",
    "label": "(list of string) 所有可選的標籤"
}
```

（value欄位的字串只是說明文字，祥細型別在括號內，或者參見預設的`workspace/setting.json`）