import cv2
import numpy as np
import mss
import pyautogui
import time
import os
import winsound

# ================= ⚡ 战术配置 =================
TEMPLATE_PATH = "target.png"
# 边缘匹配的阈值通常较低，因为线条很细
THRESHOLD = 0.5 
# 扫描区域 (全屏或局部)
SCAN_REGION = None 
COOLDOWN = 2
# ===============================================

def visual_hunt_canny():
    if not os.path.exists(TEMPLATE_PATH):
        print("❌ 未找到模板图片")
        return

    # 1. 预处理模板：读取 -> 灰度 -> 边缘检测
    template_raw = cv2.imread(TEMPLATE_PATH, 0) # 0 = Gray
    # Canny 参数 (50, 200) 是经验值，用于提取文字轮廓
    template_edge = cv2.Canny(template_raw, 50, 200)
    
    h, w = template_edge.shape[:2]

    print("=== 👁️ 视觉猎手 v3.0 (Canny边缘版) ===")
    print("策略：忽略背景色，只比对文字轮廓")

    with mss.mss() as sct:
        monitor = SCAN_REGION if SCAN_REGION else sct.monitors[1]
        last_click_time = 0

        while True:
            try:
                # 2. 截屏 -> 灰度
                img_np = np.array(sct.grab(monitor))
                img_gray = cv2.cvtColor(img_np, cv2.COLOR_BGRA2GRAY)
                
                # 3. 对屏幕图像也做边缘检测
                screen_edge = cv2.Canny(img_gray, 50, 200)

                # 4. 匹配两个“黑底白线”的图
                res = cv2.matchTemplate(screen_edge, template_edge, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                # 调试：打印相似度看看 (边缘匹配通常在 0.5 - 0.8 之间就算很高了)
                # if max_val > 0.3: print(f"当前边缘相似度: {max_val:.2f}")

                if max_val >= THRESHOLD:
                    current_time = time.time()
                    if current_time - last_click_time > COOLDOWN:
                        click_x = monitor['left'] + max_loc[0] + w // 2
                        click_y = monitor['top'] + max_loc[1] + h // 2

                        print(f"🔥 [轮廓命中] 相似度:{max_val:.2f} | 坐标:({click_x}, {click_y})")
                        pyautogui.click(click_x, click_y)
                        last_click_time = current_time
            
            except Exception as e:
                pass
            
            # time.sleep(0.01)

if __name__ == "__main__":
    visual_hunt_canny()