import cv2
from pyzbar.pyzbar import decode
from selenium import webdriver
import threading
import numpy as np

# 初始化相機
cap = cv2.VideoCapture(0)

# 初始化 Safari 驅動程式
driver = webdriver.Safari()

barcode_counts = {}  # 每個條碼的出現次數
last_searched_barcode = None  # 上次搜尋的條碼

def search_most_frequent_barcode():
    global last_searched_barcode
    if barcode_counts:
        # 找出被掃描得最多次的條碼
        most_frequent_barcode = max(barcode_counts, key=barcode_counts.get)
        
        # 檢查此條碼是否為上次搜尋的條碼
        if most_frequent_barcode != last_searched_barcode:
            search_url = "https://www.google.com/search?q=" + most_frequent_barcode
            driver.get(search_url)
            last_searched_barcode = most_frequent_barcode

    # 每2秒檢查一次
    threading.Timer(2, search_most_frequent_barcode).start()

def process_barcodes(frame):
    barcodes = decode(frame)
    for barcode in barcodes:
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type

        # 更新barcode_counts
        barcode_counts[barcode_data] = barcode_counts.get(barcode_data, 0) + 1

        # 只針對 EAN13 和 EAN8 類型的條碼進行操作
        if barcode_type in ['EAN13', 'EAN8']:
            # 繪製邊界
            pts = np.array([(int(point.x), int(point.y)) for point in barcode.polygon], dtype=np.int32)
            cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

            # 在條碼上方顯示條碼資料（ID）
            x, y = barcode.rect.left, barcode.rect.top
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, barcode_data, (x, y-10), font, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
    
    cv2.imshow('Barcode Scanner', frame)

# 啟動定時器
search_most_frequent_barcode()

while True:
    ret, frame = cap.read()
    if ret:
        process_barcodes(frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
