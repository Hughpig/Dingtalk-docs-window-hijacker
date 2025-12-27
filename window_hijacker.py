import win32gui
import win32process
import uiautomation as auto
import time
import pyperclip
import os
import psutil
import ctypes

# ================= 1. 核心：DPI 感知 =================
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    ctypes.windll.user32.SetProcessDPIAware()

# ================= 2. 配置区 =================
KEYWORDS = ["表单", "钉钉文档", "智能填表","预约", "填写", "问卷", "文档"]
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
# ============================================

class TabAwareHijacker:
    def __init__(self):
        self.processed_tasks = set()
        auto.SetGlobalSearchTimeout(0.5)

    def get_process_name(self, hwnd):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name().lower()
        except: return ""

    def solve_via_handle(self, hwnd, title):

        try:
            win = auto.ControlFromHandle(hwnd)
            if not win.Exists(0): return False
            
            print(f"🚨 [捕获] {title}")
            win.SetActive()
            rect = win.BoundingRectangle
            
            share_btn = win.ButtonControl(searchDepth=15, Name="分享")
            if share_btn.Exists(0.2):
                share_btn.Click(simulateMove=False)
                print("   - ✅ UI点击【分享】")
            else:
                auto.Click(rect.right - 85, rect.top + 75)
                print("   - ✅ 坐标点击【分享】")

            found_copy = False
            start_wait = time.time()
            while time.time() - start_wait < 1.5:
                copy_btn = auto.ButtonControl(searchDepth=10, Name="复制链接")
                if not copy_btn.Exists(0):
                    copy_btn = auto.MenuItemControl(searchDepth=10, Name="复制链接")
                
                if copy_btn.Exists(0):
                    copy_btn.Click(simulateMove=False)
                    print(f"   - ✅ 复制成功 (耗时: {int((time.time()-start_wait)*1000)}ms)")
                    found_copy = True
                    break
                time.sleep(0.1)

            if found_copy:
                time.sleep(0.2)
                url = pyperclip.paste().strip()
                if url.startswith("http"):
                    print(f"   - 🚀 弹射: {url[:30]}...")
                    os.startfile(EDGE_PATH, "open", url)
                    win.GetWindowPattern().Close()
                    return True
            
            return False
                
        except Exception as e:
            print(f"   - ⚠️ 逻辑中断: {e}")
            return False

    def scan(self):
        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd): return
            
            title = win32gui.GetWindowText(hwnd)
            if (hwnd, title) in self.processed_tasks: return

            class_name = win32gui.GetClassName(hwnd)
            process_name = self.get_process_name(hwnd)

            if "dingtalk" in process_name:
                if title == "钉钉" or title == "": return
                
                if "WebBrowserView" in class_name or any(k in title for k in KEYWORDS):
                    # 执行劫持
                    if self.solve_via_handle(hwnd, title):
                        self.processed_tasks.add((hwnd, title))
                    else:
                        self.processed_tasks.add((hwnd, title))

        win32gui.EnumWindows(callback, None)

    def run(self):
        print("=== 🛡️ 钉钉劫持器 ===")
        while True:
            self.scan()
            time.sleep(1)

if __name__ == "__main__":
    app = TabAwareHijacker()
    app.run()
