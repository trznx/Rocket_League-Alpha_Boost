import cv2
import mss
import numpy as np
import time
import json
import os

def run_calibration(callback=None):
    if callback: callback("1. Open the game and enter Freeplay.\n2. Empty your boost to 0.\n3. You have 5 seconds, switch to game now!")
    print("="*50)
    print("  ALPHA BOOST - CALIBRATION TOOL")
    print("="*50)
    
    for i in range(5, 0, -1):
        print(f"{i} seconds...")
        if callback: callback(f"Taking screenshot in {i} seconds...")
        time.sleep(1)

    if callback: callback("Taking screenshot...")

    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img_bgra = np.array(sct.grab(monitor))

    img = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
    cv2.imwrite("debug_tam_ekran.png", img)

    if callback: callback("Screenshot taken! A window will open.\nSelect the '0' digit with your mouse.\nPress ENTER or SPACE to save.")

    cv2.namedWindow("Select 0 digit and press ENTER", cv2.WINDOW_NORMAL)
    r = cv2.selectROI("Select 0 digit and press ENTER", img, showCrosshair=True, fromCenter=False)
    cv2.destroyAllWindows()

    if r[2] == 0 or r[3] == 0:
        if callback: callback("Calibration cancelled.")
        return False

    x, y, w, h = int(r[0]), int(r[1]), int(r[2]), int(r[3])
    
    cropped = img[y:y+h, x:x+w]
    cv2.imwrite("debug_kesilmis_bolge.png", cropped)

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    max_val = np.max(gray)
    mean_val = np.mean(gray)

    if max_val < 30:
        if callback: callback("ERROR: Selected region is too dark! Boost UI not found.")
        return False

    dynamic_thresh = int(mean_val + (max_val - mean_val) * 0.7)
    _, thresh = cv2.threshold(gray, dynamic_thresh, 255, cv2.THRESH_BINARY)

    cv2.imwrite("template_0.png", thresh)
    
    config = {"left": x, "top": y, "width": w, "height": h, "threshold": dynamic_thresh}
    with open("config.json", "w") as f:
        json.dump(config, f)

    if callback: callback("Calibration SUCCESSFUL!\nYou can now use the Alpha Boost Engine.")
    return True

if __name__ == '__main__':
    run_calibration()
